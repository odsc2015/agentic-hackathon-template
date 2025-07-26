//
//  BenefitCardView.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//


//
//  BenefitCardView.swift
//  app
//

import SwiftUI

struct BenefitCardView: View {
    let eligibilityResponse: EligibilityResponse?
    
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            HStack {
                Text("Benefits Summary")
                    .font(.headline)
                    .foregroundColor(.primaryBlue)
                
                Spacer()
                
                if let status = eligibilityResponse?.getEligibilityStatus() {
                    HStack {
                        Circle()
                            .fill(status.contains("Active") ? Color.green : Color.orange)
                            .frame(width: 10, height: 10)
                        
                        Text(status)
                            .font(.subheadline)
                            .foregroundColor(.black)
                    }
                }
            }
            
            if let planName = eligibilityResponse?.getPlanName() {
                Text(planName)
                    .font(.subheadline)
                    .foregroundColor(.textGray)
            }
            
            Divider()
            
            // Insurance Provider
            if let payerName = eligibilityResponse?.payer?.name {
                BenefitInfoRow(title: "Insurance Provider", value: payerName)
            }
            
            // Insurance Contact
            if let phoneNumber = eligibilityResponse?.getPayerPhoneNumber() {
                BenefitInfoRow(title: "Customer Service", value: formatPhoneNumber(phoneNumber))
            }
            
            // Plan Dates
            if let planBegin = eligibilityResponse?.getFormattedPlanBeginDate(),
               let planEnd = eligibilityResponse?.getFormattedPlanEndDate() {
                BenefitInfoRow(title: "Plan Period", value: "\(planBegin) - \(planEnd)")
            }
            
            Divider()
            
            // Cost Summary
            Text("Cost Summary")
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(.primaryBlue)
                .padding(.top, 5)
            
            // Deductible
            if let deductible = eligibilityResponse?.getDeductibleAmount() {
                BenefitInfoRow(title: "Deductible", value: formatCurrency(deductible))
            }
            
            // Out of Pocket Maximum
            if let outOfPocket = eligibilityResponse?.getOutOfPocketMaximum() {
                BenefitInfoRow(title: "Out of Pocket Max", value: formatCurrency(outOfPocket))
            }
            
            // Coinsurance
            if let coinsurance = eligibilityResponse?.getCoinsurancePercentage() {
                BenefitInfoRow(title: "Coinsurance", value: coinsurance)
            }
            
            // Co-pays
            if let benefits = eligibilityResponse?.benefitsInformation {
                // Get copays
                let copays = benefits.filter { $0.name == "Co-Payment" }
                
                if !copays.isEmpty {
                    Divider()
                    
                    Text("Co-Payments")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.primaryBlue)
                        .padding(.top, 5)
                    
                    ForEach(copays, id: \.code) { copay in
                        if let serviceType = copay.serviceTypes?.first, let amount = copay.benefitAmount {
                            BenefitInfoRow(title: serviceType, value: formatCurrency(amount))
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
        .padding(.horizontal)
    }
    
    // Format currency string
    private func formatCurrency(_ value: String) -> String {
        if let amount = Double(value) {
            let formatter = NumberFormatter()
            formatter.numberStyle = .currency
            formatter.currencyCode = "USD"
            return formatter.string(from: NSNumber(value: amount)) ?? "$\(value)"
        }
        return "$\(value)"
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

// Helper row for displaying benefit information
struct BenefitInfoRow: View {
    var title: String
    var value: String
    
    var body: some View {
        HStack(alignment: .top) {
            Text(title)
                .font(.subheadline)
                .foregroundColor(.textGray)
                .frame(width: 130, alignment: .leading)
            
            Spacer()
            
            Text(value)
                .font(.subheadline)
                .foregroundColor(.black)
                .multilineTextAlignment(.trailing)
        }
        .padding(.vertical, 2)
    }
}

struct BenefitCardView_Previews: PreviewProvider {
    static var previews: some View {
        ScrollView {
            BenefitCardView(eligibilityResponse: nil)
        }
        .background(Color.backgroundGray)
        .previewLayout(.sizeThatFits)
    }
}