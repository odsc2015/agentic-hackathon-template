//
//  AuthViewModel.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//

import Foundation
import FirebaseAuth
import FirebaseCore
import FirebaseFirestore

class AuthViewModel: ObservableObject {
    @Published var email = ""
    @Published var password = ""
    @Published var confirmPassword = ""
    @Published var firstName = ""
    @Published var lastName = ""
    @Published var isLoading = false
    @Published var errorMessage = ""
    @Published var isAuthenticated = false
    @Published var isOnboardingComplete = false
    
    // Eligibility status
    @Published var eligibilityStatus: String?
    @Published var isEligibilityChecking = false
    
    init() {
        checkAuthStatus()
        checkOnboardingStatus()
    }
    
    func checkAuthStatus() {
        isAuthenticated = Auth.auth().currentUser != nil
    }
    
    func checkOnboardingStatus() {
        if isAuthenticated {
            let profile = UserDefaultsManager.shared.getUserProfile()
            isOnboardingComplete = profile?.insuranceProvider != nil
        } else {
            isOnboardingComplete = false
        }
    }
    
    func login() {
        guard !email.isEmpty, !password.isEmpty else {
            errorMessage = "Please fill in all fields"
            return
        }
        
        isLoading = true
        errorMessage = ""
        
        Auth.auth().signIn(withEmail: email, password: password) { [weak self] result, error in
            guard let self = self else { return }
            
            self.isLoading = false
            
            if let error = error {
                self.errorMessage = error.localizedDescription
                return
            }
            
            // Check if user has a profile in Firestore
            if let userId = Auth.auth().currentUser?.uid {
                Firestore.firestore().collection("users").document(userId).getDocument { [weak self] document, error in
                    guard let self = self else { return }
                    
                    if let document = document, document.exists,
                       let data = document.data(),
                       let firstName = data["firstName"] as? String,
                       let lastName = data["lastName"] as? String {
                        
                        // Get existing profile or create new one with data from Firestore
                        let profile = UserProfile(firstName: firstName, lastName: lastName)
                        UserDefaultsManager.shared.saveUserProfile(profile)
                    }
                    
                    self.isAuthenticated = true
                    self.checkOnboardingStatus()
                }
            } else {
                self.isAuthenticated = true
                self.checkOnboardingStatus()
            }
        }
    }
    
    func signup() {
        guard !email.isEmpty, !password.isEmpty, !confirmPassword.isEmpty,
              !firstName.isEmpty, !lastName.isEmpty else {
            errorMessage = "Please fill in all fields"
            return
        }
        
        guard password == confirmPassword else {
            errorMessage = "Passwords do not match"
            return
        }
        
        isLoading = true
        errorMessage = ""
        
        Auth.auth().createUser(withEmail: email, password: password) { [weak self] result, error in
            guard let self = self else { return }
            
            self.isLoading = false
            
            if let error = error {
                self.errorMessage = error.localizedDescription
                return
            }
            
            // Create user profile
            guard let user = result?.user else { return }
            
            let userData = [
                "firstName": self.firstName,
                "lastName": self.lastName,
                "email": self.email,
                "createdAt": Timestamp()
            ]
            
            Firestore.firestore().collection("users").document(user.uid).setData(userData) { [weak self] error in
                guard let self = self else { return }
                
                if let error = error {
                    self.errorMessage = error.localizedDescription
                    return
                }
                
                // Save to local storage
                let userProfile = UserProfile(firstName: self.firstName, lastName: self.lastName)
                UserDefaultsManager.shared.saveUserProfile(userProfile)
                
                self.isAuthenticated = true
                self.isOnboardingComplete = false // Needs to complete onboarding
            }
        }
    }
    
    func signOut() {
        do {
            try Auth.auth().signOut()
            isAuthenticated = false
            isOnboardingComplete = false
            UserDefaultsManager.shared.clearAllData() // Clear all local storage
            resetFields()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
    
    func resetFields() {
        email = ""
        password = ""
        confirmPassword = ""
        firstName = ""
        lastName = ""
        errorMessage = ""
    }
    
    func completeOnboarding(insuranceProvider: String, memberID: String, dateOfBirth: Date) {
        isLoading = true
        
        // Get existing profile or create new one
        guard let profile = UserDefaultsManager.shared.getUserProfile() else {
            isLoading = false
            errorMessage = "User profile not found"
            return
        }
        
        // Start eligibility check
        isEligibilityChecking = true
        
        // Call eligibility service
        EligibilityService.shared.checkEligibility(
            firstName: profile.firstName,
            lastName: profile.lastName,
            dateOfBirth: dateOfBirth,
            memberId: memberID,
            insuranceProvider: insuranceProvider
        ) { [weak self] result in
            guard let self = self else { return }
            
            switch result {
            case .success(let response):
                self.handleEligibilitySuccess(response: response, profile: profile, insuranceProvider: insuranceProvider, memberID: memberID, dateOfBirth: dateOfBirth)
                self.isEligibilityChecking = false
                self.isLoading = false
                
            case .failure(let error):
                print("⚠️ Primary eligibility check failed: \(error.localizedDescription)")
                
                // Try with the alternative method using exact JSON string
                print("⚠️ Trying alternative method with exact JSON string...")
                EligibilityService.shared.checkEligibilityWithExactJSON(
                    firstName: profile.firstName,
                    lastName: profile.lastName,
                    dateOfBirth: dateOfBirth,
                    memberId: memberID,
                    insuranceProvider: insuranceProvider
                ) { [weak self] result in
                    guard let self = self else { return }
                    
                    self.isEligibilityChecking = false
                    self.isLoading = false
                    
                    switch result {
                    case .success(let response):
                        self.handleEligibilitySuccess(response: response, profile: profile, insuranceProvider: insuranceProvider, memberID: memberID, dateOfBirth: dateOfBirth)
                        
                    case .failure(let error):
                        self.errorMessage = "Eligibility check failed: \(error.localizedDescription)"
                        print("⚠️ Alternative eligibility check also failed: \(error)")
                        
                        // Even if eligibility check fails, still complete onboarding
                        self.completeOnboardingWithoutEligibility(profile: profile, insuranceProvider: insuranceProvider, memberID: memberID, dateOfBirth: dateOfBirth)
                    }
                }
            }
        }
    }
    
    // Helper method to handle successful eligibility check
    private func handleEligibilitySuccess(
        response: EligibilityResponse,
        profile: UserProfile,
        insuranceProvider: String,
        memberID: String,
        dateOfBirth: Date
    ) {
        // Store eligibility status
        let eligibilityStatus = response.getEligibilityStatus()
        self.eligibilityStatus = eligibilityStatus
        
        // Update profile with insurance information
        var updatedProfile = profile
        updatedProfile.insuranceProvider = insuranceProvider
        updatedProfile.memberID = memberID
        updatedProfile.dateOfBirth = dateOfBirth
        updatedProfile.eligibilityStatus = eligibilityStatus
        updatedProfile.lastEligibilityCheck = Date()
        
        // Save updated profile
        UserDefaultsManager.shared.saveUserProfile(updatedProfile)
        
        // Save only the essential eligibility data
        UserDefaultsManager.shared.saveEssentialEligibilityDataFromResponse(response)
        
        // Mark onboarding as complete
        self.isOnboardingComplete = true
        
        // Update Firestore
        if let userId = Auth.auth().currentUser?.uid {
            let insuranceData = [
                "insuranceProvider": insuranceProvider,
                "memberID": memberID,
                "dateOfBirth": dateOfBirth,
                "eligibilityStatus": eligibilityStatus
            ] as [String: Any]
            
            Firestore.firestore().collection("users").document(userId).updateData(insuranceData) { error in
                if let error = error {
                    print("Error updating Firestore: \(error.localizedDescription)")
                }
            }
        }
    }
    
    // Helper method to complete onboarding without eligibility check
    private func completeOnboardingWithoutEligibility(
        profile: UserProfile,
        insuranceProvider: String,
        memberID: String,
        dateOfBirth: Date
    ) {
        var updatedProfile = profile
        updatedProfile.insuranceProvider = insuranceProvider
        updatedProfile.memberID = memberID
        updatedProfile.dateOfBirth = dateOfBirth
        updatedProfile.eligibilityStatus = "Unknown"
        updatedProfile.lastEligibilityCheck = Date()
        UserDefaultsManager.shared.saveUserProfile(updatedProfile)
        self.isOnboardingComplete = true
    }
}
