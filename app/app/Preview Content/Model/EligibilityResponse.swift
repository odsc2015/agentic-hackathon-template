//
//  EligibilityResponse.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.

import Foundation

// MARK: - Eligibility Response Models
struct EligibilityResponse: Codable {
    let meta: Meta?
    let controlNumber: String?
    let reassociationKey: String?
    let tradingPartnerServiceId: String?
    
    let subscriber: Subscriber?
    let provider: Provider?
    let payer: Payer?
    
    let planInformation: PlanInformation?
    let planDateInformation: PlanDateInformation?
    let planStatus: [PlanStatus]?
    let benefitsInformation: [BenefitInformation]?
    
    let errors: [String]?
    let eligibilitySearchId: String?
    
    let status: String?
    let benefits: [Benefit]?
    
    // MARK: - Meta
    struct Meta: Codable {
        let senderId: String?
        let submitterId: String?
        let applicationMode: String?
        let traceId: String?
        let outboundTraceId: String?
    }
    
    // MARK: - Provider
    struct Provider: Codable {
        let providerName: String?
        let providerOrgName: String?
        let entityIdentifier: String?
        let entityType: String?
        let npi: String?
    }
    
    // MARK: - Subscriber
    struct Subscriber: Codable {
        let memberId: String?
        let firstName: String?
        let lastName: String?
        let middleName: String?
        let gender: String?
        let entityIdentifier: String?
        let entityType: String?
        let dateOfBirth: String?
        let groupNumber: String?
        let address: Address?
        
        struct Address: Codable {
            let address1: String?
            let city: String?
            let state: String?
            let postalCode: String?
        }
    }
    
    // MARK: - Payer
    struct Payer: Codable {
        let entityIdentifier: String?
        let entityType: String?
        let lastName: String?
        let name: String?
        let federalTaxpayersIdNumber: String?
        let contactInformation: ContactInformation?
        
        struct ContactInformation: Codable {
            let contacts: [Contact]?
            
            struct Contact: Codable {
                let communicationMode: String?
                let communicationNumber: String?
            }
        }
    }
    
    // MARK: - Plan Information
    struct PlanInformation: Codable {
        let groupNumber: String?
        let groupDescription: String?
    }
    
    // MARK: - Plan Date Information
    struct PlanDateInformation: Codable {
        let planBegin: String?
        let planEnd: String?
        let eligibilityBegin: String?
    }
    
    // MARK: - Plan Status
    struct PlanStatus: Codable {
        let statusCode: String?
        let status: String?
        let planDetails: String?
        let serviceTypeCodes: [String]?
    }
    
    // MARK: - Benefit Information
    struct BenefitInformation: Codable {
        let code: String?
        let name: String?
        let serviceTypeCodes: [String]?
        let serviceTypes: [String]?
        let planCoverage: String?
        let coverageLevelCode: String?
        let coverageLevel: String?
        let timeQualifierCode: String?
        let timeQualifier: String?
        let benefitAmount: String?
        let benefitPercent: String?
        let inPlanNetworkIndicatorCode: String?
        let inPlanNetworkIndicator: String?
        let authOrCertIndicator: String?
        let additionalInformation: [AdditionalInfo]?
        
        struct AdditionalInfo: Codable {
            let description: String?
        }
    }
    
    // For backward compatibility
    struct Benefit: Codable {
        let coverageLevel: String?
        let serviceType: String?
        let insuranceType: String?
        let inNetwork: Bool?
        let timeQualifiers: [TimeQualifier]?
        
        struct TimeQualifier: Codable {
            let qualifier: String?
            let amount: Amount?
            
            struct Amount: Codable {
                let value: String?
                let currency: String?
            }
        }
    }
    
    // MARK: - Helper Methods
    
    // Get eligibility status from response
    func getEligibilityStatus() -> String {
        // First check in planStatus
        if let planStatus = planStatus?.first, let status = planStatus.status {
            return status
        }
        
        // Fall back to old status field
        return status ?? "Active"
    }
    
    // Get payer phone number
    func getPayerPhoneNumber() -> String? {
        return payer?.contactInformation?.contacts?.first(where: { $0.communicationMode == "Telephone" })?.communicationNumber
    }
    
    // Get payer website
    func getPayerWebsite() -> String? {
        return payer?.contactInformation?.contacts?.first(where: { $0.communicationMode == "Uniform Resource Locator (URL)" })?.communicationNumber
    }
    
    // Get plan name
    func getPlanName() -> String? {
        return planStatus?.first?.planDetails
    }
    
    // Get deductible amount
    func getDeductibleAmount() -> String? {
        return benefitsInformation?.first(where: { $0.name == "Deductible" })?.benefitAmount
    }
    
    // Get out of pocket maximum
    func getOutOfPocketMaximum() -> String? {
        return benefitsInformation?.first(where: { $0.name == "Out of Pocket (Stop Loss)" })?.benefitAmount
    }
    
    // Get coinsurance percentage
    func getCoinsurancePercentage() -> String? {
        if let benefitPercent = benefitsInformation?.first(where: { $0.name == "Co-Insurance" })?.benefitPercent {
            // Convert decimal to percentage (e.g., "0.2" to "20%")
            if let decimal = Double(benefitPercent) {
                return "\(Int(decimal * 100))%"
            }
            return benefitPercent
        }
        return nil
    }
    
    // Format plan dates
    func formatPlanDate(dateString: String?) -> String? {
        guard let dateString = dateString, dateString.count == 8 else { return nil }
        
        let year = dateString.prefix(4)
        let month = dateString.dropFirst(4).prefix(2)
        let day = dateString.dropFirst(6).prefix(2)
        
        return "\(month)/\(day)/\(year)"
    }
    
    // Get formatted plan begin date
    func getFormattedPlanBeginDate() -> String? {
        return formatPlanDate(dateString: planDateInformation?.planBegin)
    }
    
    // Get formatted plan end date
    func getFormattedPlanEndDate() -> String? {
        return formatPlanDate(dateString: planDateInformation?.planEnd)
    }
}



