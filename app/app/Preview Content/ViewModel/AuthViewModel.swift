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

// MARK: - AuthViewModel
class AuthViewModel: ObservableObject {
    @Published var email = ""
    @Published var password = ""
    @Published var confirmPassword = ""
    @Published var firstName = ""
    @Published var lastName = ""
    @Published var isLoading = false
    @Published var errorMessage = ""
    @Published var isAuthenticated = false
    
    init() {
        checkAuthStatus()
    }
    
    func checkAuthStatus() {
        isAuthenticated = Auth.auth().currentUser != nil
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
            
            self.isAuthenticated = true
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
            
            Firestore.firestore().collection("users").document(user.uid).setData(userData) { error in
                if let error = error {
                    self.errorMessage = error.localizedDescription
                    return
                }
                
                self.isAuthenticated = true
            }
        }
    }
    
    func signOut() {
        do {
            try Auth.auth().signOut()
            isAuthenticated = false
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
}
