//
//  HomeView.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//

import SwiftUI

struct HomeView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @State private var userProfile: UserProfile?
    @State private var eligibilityData: SimplifiedEligibilityData?
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Header
                    VStack(spacing: 5) {
                        Text("Welcome to inSure")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundColor(.primaryBlue)
                        
                        if let profile = userProfile {
                            Text("Hello, \(profile.firstName) \(profile.lastName)")
                                .font(.title3)
                                .foregroundColor(.textGray)
                        }
                    }
                    .padding(.top, 20)
                    
                    // Profile Card
                    VStack(alignment: .leading, spacing: 15) {
                        Text("Your Profile")
                            .font(.headline)
                            .foregroundColor(.primaryBlue)
                        
                        if let profile = userProfile {
                            // Personal Info
                            ProfileInfoRow(title: "Name", value: "\(profile.firstName) \(profile.lastName)")
                            
                            Divider()
                            
                            // Insurance Info
                            if let provider = profile.insuranceProvider {
                                ProfileInfoRow(title: "Insurance Provider", value: provider)
                            }
                            
                            if let memberID = profile.memberID {
                                ProfileInfoRow(title: "Member ID", value: memberID)
                            }
                            
                            if let dob = profile.formattedDateOfBirth {
                                ProfileInfoRow(title: "Date of Birth", value: dob)
                            }
                            
                            // Display eligibility status if available
                            if let status = eligibilityData?.getEligibilityStatus() {
                                Divider()
                                
                                HStack {
                                    Text("Eligibility Status")
                                        .font(.subheadline)
                                        .foregroundColor(.textGray)
                                        .frame(width: 130, alignment: .leading)
                                    
                                    Spacer()
                                    
                                    HStack {
                                        Circle()
                                            .fill(status == "Active Coverage" ? Color.green : Color.orange)
                                            .frame(width: 10, height: 10)
                                        
                                        Text(status)
                                            .font(.subheadline)
                                            .foregroundColor(.black)
                                    }
                                }
                                .padding(.vertical, 4)
                                
                                // Format and display last checked time
                                let formattedDate: String = {
                                    let formatter = DateFormatter()
                                    formatter.dateStyle = .medium
                                    formatter.timeStyle = .short
                                    return formatter.string(from: eligibilityData?.lastChecked ?? Date())
                                }()
                                
                                Text("Last checked: \(formattedDate)")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                                    .frame(maxWidth: .infinity, alignment: .trailing)
                            }
                        } else {
                            Text("Profile information not available")
                                .foregroundColor(.textGray)
                        }
                    }
                    .padding()
                    .background(Color.white)
                    .cornerRadius(12)
                    .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
                    .padding(.horizontal)
                    
                    // Benefits Card
                    if let eligibilityData = eligibilityData {
                        SimplifiedBenefitCardView(eligibilityData: eligibilityData)
                    }
                    
                    // Insurance Card Section
                    VStack(alignment: .leading, spacing: 15) {
                        // Heading with more padding above
                        Text("Your Insurance Card")
                            .font(.headline)
                            .foregroundColor(.primaryBlue)
                            .padding(.top, 10)
                            .padding(.bottom, 5)
                        
                        if let profile = userProfile, let provider = profile.insuranceProvider {
                            // Digital Insurance Card - contained in its own VStack for better spacing
                            VStack {
                                ZStack {
                                    // Card background
                                    RoundedRectangle(cornerRadius: 12)
                                        .fill(LinearGradient(
                                            gradient: Gradient(colors: [.primaryBlue, .secondaryBlue]),
                                            startPoint: .topLeading,
                                            endPoint: .bottomTrailing))
                                        .shadow(color: Color.black.opacity(0.2), radius: 8, x: 0, y: 4)
                                    
                                    VStack(alignment: .leading, spacing: 12) {
                                        // Provider logo/name
                                        HStack {
                                            Image(systemName: "shield.checkerboard")
                                                .resizable()
                                                .scaledToFit()
                                                .frame(width: 30, height: 30)
                                                .foregroundColor(.white)
                                            
                                            // Use payer name from eligibility data if available
                                            Text(eligibilityData?.payerInfo?.name ?? provider)
                                                .font(.headline)
                                                .foregroundColor(.white)
                                            
                                            Spacer()
                                        }
                                        
                                        Spacer()
                                        
                                        // Member info
                                        Group {
                                            HStack {
                                                Text("Member")
                                                    .font(.caption)
                                                    .foregroundColor(.white.opacity(0.8))
                                                Spacer()
                                                Text("ID")
                                                    .font(.caption)
                                                    .foregroundColor(.white.opacity(0.8))
                                            }
                                            
                                            HStack {
                                                Text("\(profile.firstName) \(profile.lastName)")
                                                    .font(.subheadline)
                                                    .fontWeight(.semibold)
                                                    .foregroundColor(.white)
                                                Spacer()
                                                if let memberID = profile.memberID {
                                                    Text(memberID)
                                                        .font(.subheadline)
                                                        .fontWeight(.semibold)
                                                        .foregroundColor(.white)
                                                }
                                            }
                                        }
                                        
                                        Spacer()
                                        
                                        // Plan info
                                        Group {
                                            Text("Plan Information")
                                                .font(.caption)
                                                .foregroundColor(.white.opacity(0.8))
                                            
                                            // Use plan details from eligibility data if available
                                            Text(eligibilityData?.getPlanName() ?? "Standard Plan")
                                                .font(.subheadline)
                                                .fontWeight(.semibold)
                                                .foregroundColor(.white)
                                        }
                                        
                                        Spacer()
                                        
                                        // Card footer
                                        HStack {
                                            // QR code placeholder
                                            Image(systemName: "qrcode")
                                                .resizable()
                                                .scaledToFit()
                                                .frame(width: 40, height: 40)
                                                .foregroundColor(.white)
                                            
                                            Spacer()
                                            
                                            VStack(alignment: .trailing) {
                                                Text("Customer Service")
                                                    .font(.caption)
                                                    .foregroundColor(.white.opacity(0.8))
                                                // Use phone from eligibility data if available
                                                if let phone = eligibilityData?.getPayerPhoneNumber() {
                                                    Text(formatPhoneNumber(phone))
                                                        .font(.footnote)
                                                        .fontWeight(.semibold)
                                                        .foregroundColor(.white)
                                                } else {
                                                    Text("1-800-123-4567")
                                                        .font(.footnote)
                                                        .fontWeight(.semibold)
                                                        .foregroundColor(.white)
                                                }
                                            }
                                        }
                                    }
                                    .padding()
                                }
                                .frame(height: 300)
                            }
                            .padding(.top, 5) // Add space between heading and card
                        } else {
                            Text("Insurance card information not available")
                                .foregroundColor(.textGray)
                                .padding()
                        }
                    }
                    .padding()
                    .background(Color.white)
                    .cornerRadius(12)
                    .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
                    .padding(.horizontal)
                    
                    // Add extra padding at the bottom to ensure the card is fully visible
                    Spacer(minLength: 30)
                    
                    InSureButton(title: "Sign Out") {
                        authViewModel.signOut()
                    }
                    .padding(.horizontal)
                    .padding(.bottom, 30)
                }
                .padding(.top)
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
        }
        .onAppear {
            userProfile = UserDefaultsManager.shared.getUserProfile()
            loadEligibilityData()
        }
    }
    
    // Rest of the code remains the same
    private func loadEligibilityData() {
        // Load simplified eligibility data from UserDefaults
        eligibilityData = UserDefaultsManager.shared.getSimplifiedEligibilityData()
        
        // If no data found, create mock data for testing
        if eligibilityData == nil {
            createMockEligibilityData()
        }
    }
    
    private func createMockEligibilityData() {
        // This is for testing only - will be replaced with actual API data in production
        if let jsonString = """
        {
            "subscriberEntityIdentifier": "Insured or Subscriber",
            "tradingPartnerServiceId": "62308",
            "payerInfo": {
                "entityIdentifier": "Payer",
                "entityType": "Non-Person Entity",
                "lastName": "CHLIC",
                "name": "CHLIC",
                "federalTaxpayersIdNumber": "591056496",
                "contacts": [
                    {
                        "communicationMode": "Telephone",
                        "communicationNumber": "8664942111"
                    },
                    {
                        "communicationMode": "Uniform Resource Locator (URL)",
                        "communicationNumber": "cignaforhcp.cigna.com"
                    }
                ]
            },
            "planInfo": {
                "groupNumber": "00123874",
                "groupDescription": "ACME, Inc."
            },
            "planDates": {
                "planBegin": "20240101",
                "planEnd": "20241231",
                "eligibilityBegin": "20230101"
            },
            "planStatus": [
                {
                    "statusCode": "1",
                    "status": "Active Coverage",
                    "planDetails": "Open Access Plus",
                    "serviceTypeCodes": ["30"]
                }
            ],
            "benefits": [
                {
                    "code": "C",
                    "name": "Deductible",
                    "coverageLevel": "Individual",
                    "serviceTypes": ["Health Benefit Plan Coverage"],
                    "timeQualifier": "Calendar Year",
                    "benefitAmount": "5000",
                    "inPlanNetworkIndicator": "Yes"
                },
                {
                    "code": "G",
                    "name": "Out of Pocket (Stop Loss)",
                    "coverageLevel": "Individual",
                    "serviceTypes": ["Health Benefit Plan Coverage"],
                    "timeQualifier": "Calendar Year",
                    "benefitAmount": "10000",
                    "inPlanNetworkIndicator": "Yes"
                },
                {
                    "code": "A",
                    "name": "Co-Insurance",
                    "coverageLevel": "Individual",
                    "serviceTypes": ["Health Benefit Plan Coverage"],
                    "benefitPercent": "0.2",
                    "inPlanNetworkIndicator": "Yes"
                },
                {
                    "code": "B",
                    "name": "Co-Payment",
                    "coverageLevel": "Individual",
                    "serviceTypes": ["Professional (Physician) Visit - Office"],
                    "timeQualifier": "Visit",
                    "benefitAmount": "25",
                    "inPlanNetworkIndicator": "Yes"
                },
                {
                    "code": "B",
                    "name": "Co-Payment",
                    "coverageLevel": "Individual",
                    "serviceTypes": ["Urgent Care"],
                    "timeQualifier": "Visit",
                    "benefitAmount": "75",
                    "inPlanNetworkIndicator": "Yes"
                },
                {
                    "code": "B",
                    "name": "Co-Payment",
                    "coverageLevel": "Individual",
                    "serviceTypes": ["Emergency Services"],
                    "timeQualifier": "Visit",
                    "benefitAmount": "150",
                    "inPlanNetworkIndicator": "Yes"
                }
            ],
            "lastChecked": "2025-07-25T09:30:00Z"
        }
        """.data(using: .utf8) {
            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                let mockData = try decoder.decode(SimplifiedEligibilityData.self, from: jsonString)
                eligibilityData = mockData
                
                // Save mock data to UserDefaults for testing
                UserDefaultsManager.shared.saveSimplifiedEligibilityData(mockData)
            } catch {
                print("Error creating mock eligibility data: \(error)")
            }
        }
    }
    
    // Format phone number
    private func formatPhoneNumber(_ number: String) -> String {
        guard number.count == 10 else {
            return number
        }
        
        let areaCode = number.prefix(3)
        let firstPart = number.dropFirst(3).prefix(3)
        let lastPart = number.dropFirst(6)
        
        return "(\(areaCode)) \(firstPart)-\(lastPart)"
    }
}
