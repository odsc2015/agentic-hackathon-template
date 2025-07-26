//
//  UserDefaultsManager.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//

import Foundation

class UserDefaultsManager {
    static let shared = UserDefaultsManager()
    
    private let userProfileKey = "userProfile"
    private let eligibilityResponseKey = "eligibilityResponse"
    private let simplifiedEligibilityDataKey = "simplifiedEligibilityData"
    
    // MARK: - User Profile
    
    func saveUserProfile(_ profile: UserProfile) {
        if let encoded = try? JSONEncoder().encode(profile) {
            UserDefaults.standard.set(encoded, forKey: userProfileKey)
        }
    }
    
    func getUserProfile() -> UserProfile? {
        if let data = UserDefaults.standard.data(forKey: userProfileKey),
           let profile = try? JSONDecoder().decode(UserProfile.self, from: data) {
            return profile
        }
        return nil
    }
    
    func clearUserProfile() {
        UserDefaults.standard.removeObject(forKey: userProfileKey)
    }
    
    // MARK: - Full Eligibility Response
    
    func saveEligibilityResponse(_ response: EligibilityResponse) {
        if let encoded = try? JSONEncoder().encode(response) {
            UserDefaults.standard.set(encoded, forKey: eligibilityResponseKey)
        }
        
        saveSimplifiedEligibilityData(SimplifiedEligibilityData.from(response: response))
    }
    
    func getEligibilityResponse() -> EligibilityResponse? {
        if let data = UserDefaults.standard.data(forKey: eligibilityResponseKey),
           let response = try? JSONDecoder().decode(EligibilityResponse.self, from: data) {
            return response
        }
        return nil
    }
    
    func clearEligibilityResponse() {
        UserDefaults.standard.removeObject(forKey: eligibilityResponseKey)
    }
    
    // MARK: - Simplified Eligibility Data
    
    func saveSimplifiedEligibilityData(_ data: SimplifiedEligibilityData) {
        if let encoded = try? JSONEncoder().encode(data) {
            UserDefaults.standard.set(encoded, forKey: simplifiedEligibilityDataKey)
            
            // Print size for debugging
            let kilobytes = Double(encoded.count) / 1024.0
            print("📊 Simplified eligibility data size: \(kilobytes) KB")
        }
    }
    
    func getSimplifiedEligibilityData() -> SimplifiedEligibilityData? {
        if let data = UserDefaults.standard.data(forKey: simplifiedEligibilityDataKey),
           let simplifiedData = try? JSONDecoder().decode(SimplifiedEligibilityData.self, from: data) {
            return simplifiedData
        }
        return nil
    }
    
    func clearSimplifiedEligibilityData() {
        UserDefaults.standard.removeObject(forKey: simplifiedEligibilityDataKey)
    }
    
    // MARK: - Save Only Essential Eligibility Data
    
    func saveEssentialEligibilityDataFromResponse(_ response: EligibilityResponse) {
        let simplifiedData = SimplifiedEligibilityData.from(response: response)
        saveSimplifiedEligibilityData(simplifiedData)
    }
    
    // MARK: - Clear All Data
    
    func clearAllData() {
        clearUserProfile()
        clearEligibilityResponse()
        clearSimplifiedEligibilityData()
    }
}
