//
//  SimplifiedBenefitCardView.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//


import SwiftUI

// SimplifiedBenefitCardView for displaying the simplified eligibility data
struct SimplifiedBenefitCardView: View {
    let eligibilityData: SimplifiedEligibilityData
    
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            HStack {
                Text("Benefits Summary")
                    .font(.headline)
                    .foregroundColor(.primaryBlue)
                
                Spacer()
                
                let status = eligibilityData.getEligibilityStatus()
                HStack {
                    Circle()
                        .fill(status.contains("Active") ? Color.green : Color.orange)
                        .frame(width: 10, height: 10)
                    
                    Text(status)
                        .font(.subheadline)
                        .foregroundColor(.black)
                }
            }
            
            if let planName = eligibilityData.getPlanName() {
                Text(planName)
                    .font(.subheadline)
                    .foregroundColor(.textGray)
            }
            
            Divider()
            
            // Insurance Provider
            if let payerName = eligibilityData.payerInfo?.name {
                BenefitInfoRow(title: "Insurance Provider", value: payerName)
            }
            
            // Insurance Contact
            if let phoneNumber = eligibilityData.getPayerPhoneNumber() {
                BenefitInfoRow(title: "Customer Service", value: formatPhoneNumber(phoneNumber))
            }
            
            // Plan Dates
            if let planBegin = eligibilityData.getFormattedPlanBeginDate(),
               let planEnd = eligibilityData.getFormattedPlanEndDate() {
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
            if let deductible = eligibilityData.getDeductibleAmount() {
                BenefitInfoRow(title: "Deductible", value: formatCurrency(deductible))
            }
            
            // Out of Pocket Maximum
            if let outOfPocket = eligibilityData.getOutOfPocketMaximum() {
                BenefitInfoRow(title: "Out of Pocket Max", value: formatCurrency(outOfPocket))
            }
            
            // Coinsurance
            if let coinsurance = eligibilityData.getCoinsurancePercentage() {
                BenefitInfoRow(title: "Coinsurance", value: coinsurance)
            }
            
            // Co-pays
            let copays = eligibilityData.getCopays()
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