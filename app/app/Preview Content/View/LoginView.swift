//
//  LoginView.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//

import SwiftUI
import FirebaseCore
import FirebaseAuth

// MARK: - LoginView
struct LoginView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @State private var isSignUpMode = false
    
    var body: some View {
        ZStack {
            // Background
            Color.backgroundGray
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 30) {
                    // Logo and Header
                    VStack(spacing: 5) {
                        Image(systemName: "shield.checkerboard")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 60, height: 60)
                            .foregroundColor(.primaryBlue)
                        
                        Text("inSure.ai")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundColor(.primaryBlue)
                        
                        Text(isSignUpMode ? "Create your account" : "Sign in to your account")
                            .font(.subheadline)
                            .foregroundColor(.textGray)
                    }
                    .padding(.top, 40)
                    
                    // Form
                    VStack(spacing: 15) {
                        if isSignUpMode {
                            // Sign Up Form
                            HStack(spacing: 10) {
                                InSureTextField(placeholder: "First Name", text: $authViewModel.firstName)
                                InSureTextField(placeholder: "Last Name", text: $authViewModel.lastName)
                            }
                        }
                        
                        InSureTextField(placeholder: "Email", text: $authViewModel.email, keyboardType: .emailAddress)
                        
                        InSureTextField(placeholder: "Password", text: $authViewModel.password, isSecure: true)
                        
                        if isSignUpMode {
                            InSureTextField(placeholder: "Confirm Password", text: $authViewModel.confirmPassword, isSecure: true)
                        }
                        
                        if !authViewModel.errorMessage.isEmpty {
                            Text(authViewModel.errorMessage)
                                .font(.footnote)
                                .foregroundColor(.red)
                                .padding(.top, 5)
                        }
                        
                        // Action Buttons
                        VStack(spacing: 15) {
                            InSureButton(title: isSignUpMode ? "Sign Up" : "Sign In") {
                                if isSignUpMode {
                                    authViewModel.signup()
                                } else {
                                    authViewModel.login()
                                }
                            }
                            
                            Button(action: {
                                withAnimation {
                                    isSignUpMode.toggle()
                                    authViewModel.resetFields()
                                }
                            }) {
                                Text(isSignUpMode ? "Already have an account? Sign In" : "Don't have an account? Sign Up")
                                    .font(.footnote)
                                    .foregroundColor(.primaryBlue)
                            }
                        }
                        .padding(.top, 10)
                    }
                    .padding(.horizontal)
                    
                    Spacer(minLength: 30)
                    
                    // Footer
                    VStack(spacing: 10) {
                        Text("By continuing, you agree to inSure's")
                            .font(.caption)
                            .foregroundColor(.textGray)
                        
                        HStack(spacing: 5) {
                            Text("Terms of Service")
                                .font(.caption)
                                .foregroundColor(.primaryBlue)
                                .underline()
                            
                            Text("and")
                                .font(.caption)
                                .foregroundColor(.textGray)
                            
                            Text("Privacy Policy")
                                .font(.caption)
                                .foregroundColor(.primaryBlue)
                                .underline()
                        }
                    }
                    .padding(.bottom, 30)
                }
                .padding(.horizontal)
            }
            // Apply the keyboard dismissal to the entire view
            .dismissKeyboard()
            
            if authViewModel.isLoading {
                Color.black.opacity(0.4)
                    .ignoresSafeArea()
                
                ProgressView()
                    .scaleEffect(1.5)
                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
            }
        }
    }
}


