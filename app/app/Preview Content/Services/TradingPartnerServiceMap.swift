//
//  EligibilityService.swift
//  app
//

import Foundation

// MARK: - Trading Partner Service Map
struct TradingPartnerServiceMap {
    static let map: [String: String] = [
        "Aetna": "60054",
        "Cigna": "62308",
        "UnitedHealthcare": "87726",
        "BlueCross BlueShield of Texas": "G84980"
    ]
}

// MARK: - Eligibility Request Models
struct EligibilityRequest: Codable {
    let controlNumber: String
    let tradingPartnerServiceId: String
    let provider: Provider
    let subscriber: Subscriber
    let encounter: Encounter
    
    struct Encounter: Codable {
        let serviceTypeCodes: [String]
    }
    
    struct Provider: Codable {
        let organizationName: String
        let npi: String
    }
    
    struct Subscriber: Codable {
        let firstName: String
        let lastName: String
        let dateOfBirth: String  // Format: YYYYMMDD
        let memberId: String
    }
}

// MARK: - Eligibility Service
class EligibilityService {
    static let shared = EligibilityService()
    
    private var apiUrl: String {
        return APIKeys.eligibilityAPIURL
    }
        
    private var apiKey: String {
        return APIKeys.eligibilityAPIKey
    }
    
    // Format date to YYYYMMDD format required by the API (with no separators)
    private func formatDateForAPI(date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyyMMdd"
        return formatter.string(from: date)
    }
    
    // Helper logging function for debugging API issues
    private func logAPIRequest(request: URLRequest, jsonData: Data) {
        print("🌐 API Request URL: \(request.url?.absoluteString ?? "nil")")
        print("🌐 API Request Headers: \(request.allHTTPHeaderFields ?? [:])")
        
        if let jsonString = String(data: jsonData, encoding: .utf8) {
            print("🌐 API Request Body: \(jsonString)")
        }
    }
    
    // Log API response for debugging
    private func logAPIResponse(data: Data?, response: URLResponse?, error: Error?) {
        print("🌐 API Response Status: \((response as? HTTPURLResponse)?.statusCode ?? 0)")
        
        if let error = error {
            print("🌐 API Error: \(error.localizedDescription)")
        }
        
        if let data = data, let jsonString = String(data: data, encoding: .utf8) {
            print("🌐 API Response: \(jsonString)")
        }
    }
    
    // Check eligibility for a member
    func checkEligibility(
        firstName: String,
        lastName: String,
        dateOfBirth: Date,
        memberId: String,
        insuranceProvider: String,
        completion: @escaping (Result<EligibilityResponse, Error>) -> Void
    ) {
        // Map insurance provider to trading partner service ID
        let tradingPartnerId = TradingPartnerServiceMap.map[insuranceProvider] ?? "60054" // Default to Aetna if not found
        
        // Format date to YYYYMMDD
        let formattedDate = formatDateForAPI(date: dateOfBirth)
        
        // Use JSONHelper to create exact JSON format
        guard let jsonData = JSONHelper.createExactEligibilityJSON(
            firstName: firstName,
            lastName: lastName,
            dateOfBirth: formattedDate,
            memberId: memberId,
            tradingPartnerServiceId: tradingPartnerId
        ) else {
            completion(.failure(NSError(domain: "EligibilityService", code: 400, userInfo: [NSLocalizedDescriptionKey: "Failed to create JSON"])))
            return
        }
        
        // For debugging, print the exact JSON
        print("🌐 Exact JSON being sent:")
        print(JSONHelper.prettyPrintJSON(jsonData))
        
        // Create URL request
        var request = URLRequest(url: URL(string: apiUrl)!)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue("application/json", forHTTPHeaderField: "Accept")
        request.addValue(apiKey, forHTTPHeaderField: "Authorization")
        request.httpBody = jsonData
        
        // Log the request for debugging
        logAPIRequest(request: request, jsonData: jsonData)
        
        // Make API call
        let task = URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            guard let self = self else { return }
            
            // Log the response for debugging
            self.logAPIResponse(data: data, response: response, error: error)
            
            // Save raw response for debugging if needed
            if let responseData = data {
                self.saveRawResponse(responseData)
            }
            
            // Handle network error
            if let error = error {
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
                return
            }
            
            // Handle HTTP errors
            guard let httpResponse = response as? HTTPURLResponse else {
                DispatchQueue.main.async {
                    completion(.failure(NSError(domain: "EligibilityService", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid response"])))
                }
                return
            }
            
            // Handle HTTP status errors
            if !(200...299).contains(httpResponse.statusCode) {
                DispatchQueue.main.async {
                    completion(.failure(NSError(domain: "EligibilityService", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: "HTTP error \(httpResponse.statusCode)"])))
                }
                return
            }
            
            // Process response data
            guard let responseData = data else {
                DispatchQueue.main.async {
                    completion(.failure(NSError(domain: "EligibilityService", code: 0, userInfo: [NSLocalizedDescriptionKey: "No data received"])))
                }
                return
            }
            
            // Try to parse as EligibilityResponse
            do {
                let decoder = JSONDecoder()
                let response = try decoder.decode(EligibilityResponse.self, from: responseData)
                
                // Save only the essential data to UserDefaults
                UserDefaultsManager.shared.saveEssentialEligibilityDataFromResponse(response)
                
                DispatchQueue.main.async {
                    completion(.success(response))
                }
            } catch {
                print("⚠️ Parsing error: \(error)")
                
                // If standard parsing fails, try to extract error message
                if let jsonObject = try? JSONSerialization.jsonObject(with: responseData) as? [String: Any],
                   let errorMessage = jsonObject["message"] as? String {
                    
                    // Create simplified response with error
                    let fallbackResponse = EligibilityResponse(
                        meta: nil,
                        controlNumber: nil,
                        reassociationKey: nil,
                        tradingPartnerServiceId: nil,
                        subscriber: nil,
                        provider: nil,
                        payer: nil,
                        planInformation: nil,
                        planDateInformation: nil,
                        planStatus: nil,
                        benefitsInformation: nil,
                        errors: [errorMessage],
                        eligibilitySearchId: nil,
                        status: "Error",
                        benefits: nil
                    )
                    
                    DispatchQueue.main.async {
                        completion(.success(fallbackResponse))
                    }
                } else {
                    // If we can't even extract an error message, return the parsing error
                    DispatchQueue.main.async {
                        completion(.failure(error))
                    }
                }
            }
        }
        
        task.resume()
    }
    
    // Alternative method to check eligibility using exact JSON string
    func checkEligibilityWithExactJSON(
        firstName: String,
        lastName: String,
        dateOfBirth: Date,
        memberId: String,
        insuranceProvider: String,
        completion: @escaping (Result<EligibilityResponse, Error>) -> Void
    ) {
        // Map insurance provider to trading partner service ID
        let tradingPartnerId = TradingPartnerServiceMap.map[insuranceProvider] ?? "60054"
        
        // Format date to YYYYMMDD
        let formattedDate = formatDateForAPI(date: dateOfBirth)
        
        // Get exact JSON string
        let jsonString = JSONHelper.createExactJSONString(
            firstName: firstName,
            lastName: lastName,
            dateOfBirth: formattedDate,
            memberId: memberId,
            tradingPartnerServiceId: tradingPartnerId
        )
        
        print("🌐 Using exact JSON string: \(jsonString)")
        
        guard let jsonData = JSONHelper.dataFromJSONString(jsonString) else {
            completion(.failure(NSError(domain: "EligibilityService", code: 400, userInfo: [NSLocalizedDescriptionKey: "Failed to convert JSON string to data"])))
            return
        }
        
        // Create URL request
        var request = URLRequest(url: URL(string: apiUrl)!)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue("application/json", forHTTPHeaderField: "Accept")
        request.addValue(apiKey, forHTTPHeaderField: "Authorization")
        request.httpBody = jsonData
        
        // Log the request for debugging
        logAPIRequest(request: request, jsonData: jsonData)
        
        // Make API call
        let task = URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            guard let self = self else { return }
            
            // Process response same as in the original method
            self.logAPIResponse(data: data, response: response, error: error)
            
            // Save raw response for debugging if needed
            if let responseData = data {
                self.saveRawResponse(responseData)
            }
            
            // Handle network error
            if let error = error {
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
                return
            }
            
            // Handle HTTP errors
            guard let httpResponse = response as? HTTPURLResponse else {
                DispatchQueue.main.async {
                    completion(.failure(NSError(domain: "EligibilityService", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid response"])))
                }
                return
            }
            
            // Handle HTTP status errors
            if !(200...299).contains(httpResponse.statusCode) {
                DispatchQueue.main.async {
                    completion(.failure(NSError(domain: "EligibilityService", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: "HTTP error \(httpResponse.statusCode)"])))
                }
                return
            }
            
            // Process response data
            guard let responseData = data else {
                DispatchQueue.main.async {
                    completion(.failure(NSError(domain: "EligibilityService", code: 0, userInfo: [NSLocalizedDescriptionKey: "No data received"])))
                }
                return
            }
            
            // Try to parse as EligibilityResponse
            do {
                let decoder = JSONDecoder()
                let response = try decoder.decode(EligibilityResponse.self, from: responseData)
                
                // Save only the essential data to UserDefaults
                UserDefaultsManager.shared.saveEssentialEligibilityDataFromResponse(response)
                
                DispatchQueue.main.async {
                    completion(.success(response))
                }
            } catch {
                print("⚠️ Parsing error: \(error)")
                
                // If standard parsing fails, try to extract error message
                if let jsonObject = try? JSONSerialization.jsonObject(with: responseData) as? [String: Any],
                   let errorMessage = jsonObject["message"] as? String {
                    
                    // Create simplified response with error
                    let fallbackResponse = EligibilityResponse(
                        meta: nil,
                        controlNumber: nil,
                        reassociationKey: nil,
                        tradingPartnerServiceId: nil,
                        subscriber: nil,
                        provider: nil,
                        payer: nil,
                        planInformation: nil,
                        planDateInformation: nil,
                        planStatus: nil,
                        benefitsInformation: nil,
                        errors: [errorMessage],
                        eligibilitySearchId: nil,
                        status: "Error",
                        benefits: nil
                    )
                    
                    DispatchQueue.main.async {
                        completion(.success(fallbackResponse))
                    }
                } else {
                    // If we can't even extract an error message, return the parsing error
                    DispatchQueue.main.async {
                        completion(.failure(error))
                    }
                }
            }
        }
        
        task.resume()
    }
    
    // Save raw response to UserDefaults for debugging
    private func saveRawResponse(_ data: Data) {
        if let jsonString = String(data: data, encoding: .utf8) {
            UserDefaults.standard.set(jsonString, forKey: "lastRawEligibilityResponse")
        }
    }
    
    // Get last raw response from UserDefaults
    func getLastRawResponse() -> String? {
        return UserDefaults.standard.string(forKey: "lastRawEligibilityResponse")
    }
    
    // Load eligibility data from a saved JSON string (for testing)
    func loadEligibilityFromJSON(_ jsonString: String) -> EligibilityResponse? {
        guard let data = jsonString.data(using: .utf8) else {
            return nil
        }
        
        do {
            let decoder = JSONDecoder()
            return try decoder.decode(EligibilityResponse.self, from: data)
        } catch {
            print("Error decoding eligibility JSON: \(error)")
            return nil
        }
    }
}
