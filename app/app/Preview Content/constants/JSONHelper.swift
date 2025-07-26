//
//  for.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//

import Foundation

class JSONHelper {
    static func createExactEligibilityJSON(
        firstName: String,
        lastName: String,
        dateOfBirth: String,
        memberId: String,
        tradingPartnerServiceId: String
    ) -> Data? {
        let jsonDict: [String: Any] = [
            "controlNumber": "123456789",
            "tradingPartnerServiceId": tradingPartnerServiceId,
            "provider": [
                "organizationName": "Provider Name",
                "npi": "1999999984"
            ],
            "subscriber": [
                "firstName": firstName,
                "lastName": lastName,
                "dateOfBirth": dateOfBirth,
                "memberId": memberId
            ],
            "encounter": [
                "serviceTypeCodes": ["30"]
            ]
        ]
        
        do {
            let data = try JSONSerialization.data(withJSONObject: jsonDict, options: [])
            return data
        } catch {
            print("JSON serialization error: \(error)")
            return nil
        }
    }
    
    static func createExactJSONString(
        firstName: String,
        lastName: String,
        dateOfBirth: String,
        memberId: String,
        tradingPartnerServiceId: String
    ) -> String {
        return """
        {
          "controlNumber": "123456789",
          "tradingPartnerServiceId": "\(tradingPartnerServiceId)",
          "provider": {
            "organizationName": "Provider Name",
            "npi": "1999999984"
          },
          "subscriber": {
            "firstName": "\(firstName)",
            "lastName": "\(lastName)",
            "dateOfBirth": "\(dateOfBirth)",
            "memberId": "\(memberId)"
          },
          "encounter": {
            "serviceTypeCodes": ["30"]
          }
        }
        """
    }
    
    static func dataFromJSONString(_ jsonString: String) -> Data? {
        return jsonString.data(using: .utf8)
    }
    
    static func prettyPrintJSON(_ data: Data) -> String {
        do {
            let json = try JSONSerialization.jsonObject(with: data)
            let prettyData = try JSONSerialization.data(withJSONObject: json, options: .prettyPrinted)
            return String(data: prettyData, encoding: .utf8) ?? "Unable to format JSON"
        } catch {
            return "Invalid JSON: \(error.localizedDescription)"
        }
    }
}
