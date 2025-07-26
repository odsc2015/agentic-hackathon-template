//
//  OnboardingView.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//

import SwiftUI

struct OnboardingView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @State private var insuranceProvider: String = InsuranceProvider.aetna.rawValue
    @State private var memberID: String = ""
    @State private var dateOfBirth: Date = Calendar.current.date(byAdding: .year, value: -30, to: Date()) ?? Date()
    @State private var showDatePicker: Bool = false
    @State private var showAlert: Bool = false
    
    var body: some View {
        NavigationView {
            ZStack {
                ScrollView {
                    VStack(spacing: 25) {
                        // Header
                        VStack(spacing: 10) {
                            Image(systemName: "shield.checkerboard")
                                .resizable()
                                .scaledToFit()
                                .frame(width: 60, height: 60)
                                .foregroundColor(.primaryBlue)
                            
                            Text("Complete Your Profile")
                                .font(.largeTitle)
                                .fontWeight(.bold)
                                .foregroundColor(.primaryBlue)
                            
                            Text("Please provide your insurance information")
                                .font(.subheadline)
                                .foregroundColor(.textGray)
                                .multilineTextAlignment(.center)
                        }
                        .padding(.top, 30)
                        
                        // Form
                        VStack(alignment: .leading, spacing: 20) {
                            Text("Insurance Provider")
                                .font(.headline)
                                .foregroundColor(.primaryBlue)
                            
                            // Insurance Provider Picker
                            Menu {
                                ForEach(InsuranceProvider.allCases, id: \.self) { provider in
                                    Button(provider.rawValue) {
                                        insuranceProvider = provider.rawValue
                                    }
                                }
                            } label: {
                                HStack {
                                    Text(insuranceProvider)
                                        .foregroundColor(.black)
                                    Spacer()
                                    Image(systemName: "chevron.down")
                                        .foregroundColor(.gray)
                                }
                                .padding()
                                .background(Color.white)
                                .cornerRadius(8)
                                .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
                            }
                            
                            Text("Member ID")
                                .font(.headline)
                                .foregroundColor(.primaryBlue)
                            
                            InSureTextField(placeholder: "Enter your member ID", text: $memberID)
                            
                            Text("Date of Birth")
                                .font(.headline)
                                .foregroundColor(.primaryBlue)
                            
                            // Date of Birth Button
                            Button(action: {
                                showDatePicker = true
                            }) {
                                HStack {
                                    Text(formattedDate)
                                        .foregroundColor(.black)
                                    Spacer()
                                    Image(systemName: "calendar")
                                        .foregroundColor(.gray)
                                }
                                .padding()
                                .background(Color.white)
                                .cornerRadius(8)
                                .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
                            }
                            
                            // Display error message if any
                            if !authViewModel.errorMessage.isEmpty {
                                Text(authViewModel.errorMessage)
                                    .font(.footnote)
                                    .foregroundColor(.red)
                                    .padding(.top, 5)
                            }
                        }
                        .padding(.horizontal)
                        
                        Spacer(minLength: 30)
                        
                        // Submit Button
                        InSureButton(title: "Complete Setup") {
                            if memberID.isEmpty {
                                showAlert = true
                            } else {
                                authViewModel.completeOnboarding(
                                    insuranceProvider: insuranceProvider,
                                    memberID: memberID,
                                    dateOfBirth: dateOfBirth
                                )
                            }
                        }
                        .padding(.horizontal)
                        .padding(.bottom, 30)
                    }
                }
                .background(Color.backgroundGray.ignoresSafeArea())
                .navigationBarTitleDisplayMode(.inline)
                .navigationBarItems(leading:
                    HStack {
                        Image(systemName: "shield.checkerboard")
                            .foregroundColor(.primaryBlue)
                        Text("inSure")
                            .font(.headline)
                            .foregroundColor(.primaryBlue)
                    }
                )
                // Add sheet for date picker
                .sheet(isPresented: $showDatePicker) {
                    DatePickerSheet(date: $dateOfBirth, isPresented: $showDatePicker)
                }
                .alert(isPresented: $showAlert) {
                    Alert(
                        title: Text("Missing Information"),
                        message: Text("Please enter your member ID to continue."),
                        dismissButton: .default(Text("OK"))
                    )
                }
                .disabled(authViewModel.isLoading || authViewModel.isEligibilityChecking)
                .blur(radius: (authViewModel.isLoading || authViewModel.isEligibilityChecking) ? 3 : 0)
                
                // Loading overlay
                if authViewModel.isLoading || authViewModel.isEligibilityChecking {
                    VStack(spacing: 20) {
                        ProgressView()
                            .scaleEffect(1.5)
                            .progressViewStyle(CircularProgressViewStyle(tint: .primaryBlue))
                        
                        Text(authViewModel.isEligibilityChecking ? "Checking eligibility..." : "Loading...")
                            .font(.headline)
                            .foregroundColor(.primaryBlue)
                    }
                    .padding(30)
                    .background(Color.white)
                    .cornerRadius(12)
                    .shadow(color: Color.black.opacity(0.2), radius: 10, x: 0, y: 5)
                }
            }
        }
    }
    
    // Computed property for formatted date
    private var formattedDate: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        return formatter.string(from: dateOfBirth)
    }
}

// Date Picker Sheet
struct DatePickerSheet: View {
    @Binding var date: Date
    @Binding var isPresented: Bool
    
    var body: some View {
        NavigationView {
            VStack {
                DatePicker("Select Date", selection: $date, displayedComponents: .date)
                    .datePickerStyle(GraphicalDatePickerStyle())
                    .padding()
                
                Spacer()
            }
            .navigationBarTitle("Date of Birth", displayMode: .inline)
            .navigationBarItems(
                leading: Button("Cancel") {
                    isPresented = false
                },
                trailing: Button("Done") {
                    isPresented = false
                }
                .foregroundColor(.primaryBlue)
                .fontWeight(.bold)
            )
        }
    }
}
