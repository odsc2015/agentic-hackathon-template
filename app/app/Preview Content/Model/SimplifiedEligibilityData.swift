//
//  SimplifiedEligibilityData.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//


import Foundation

struct SimplifiedEligibilityData: Codable {
    let subscriberEntityIdentifier: String?
 
    let tradingPartnerServiceId: String?

    let payerInfo: PayerInfo?
    
    let planInfo: PlanInfo?
    let planDates: PlanDates?
    let planStatus: [PlanStatusInfo]?
    
    let benefits: [BenefitInfo]?
    
    let lastChecked: Date
    
    // MARK: - Nested models
    
    struct PayerInfo: Codable {
        let name: String?
        let lastName: String?
        let entityIdentifier: String?
        let entityType: String?
        let federalTaxpayersIdNumber: String?
        let contacts: [ContactInfo]?
    }
    
    struct ContactInfo: Codable {
        let communicationMode: String?
        let communicationNumber: String?
    }
    
    struct PlanInfo: Codable {
        let groupNumber: String?
        let groupDescription: String?
    }
    
    struct PlanDates: Codable {
        let planBegin: String?
        let planEnd: String?
        let eligibilityBegin: String?
    }
    
    struct PlanStatusInfo: Codable {
        let statusCode: String?
        let status: String?
        let planDetails: String?
        let serviceTypeCodes: [String]?
    }
    
    struct BenefitInfo: Codable {
        let code: String?
        let name: String?
        let coverageLevel: String?
        let serviceTypes: [String]?
        let planCoverage: String?
        let timeQualifier: String?
        let benefitAmount: String?
        let benefitPercent: String?
        let inPlanNetworkIndicator: String?
        
        let additionalInfo: [String]?
    }
    
    // MARK: - Factory method to create from EligibilityResponse
    
    static func from(response: EligibilityResponse) -> SimplifiedEligibilityData {
        var contacts: [ContactInfo]? = nil
        if let responseContacts = response.payer?.contactInformation?.contacts {
            contacts = responseContacts.map { contact in
                return ContactInfo(
                    communicationMode: contact.communicationMode,
                    communicationNumber: contact.communicationNumber
                )
            }
        }
        
        let payerInfo = response.payer != nil ? PayerInfo(
            name: response.payer?.name,
            lastName: response.payer?.lastName,
            entityIdentifier: response.payer?.entityIdentifier,
            entityType: response.payer?.entityType,
            federalTaxpayersIdNumber: response.payer?.federalTaxpayersIdNumber,
            contacts: contacts
        ) : nil
        
        let planInfo = response.planInformation != nil ? PlanInfo(
            groupNumber: response.planInformation?.groupNumber,
            groupDescription: response.planInformation?.groupDescription
        ) : nil
        
        let planDates = response.planDateInformation != nil ? PlanDates(
            planBegin: response.planDateInformation?.planBegin,
            planEnd: response.planDateInformation?.planEnd,
            eligibilityBegin: response.planDateInformation?.eligibilityBegin
        ) : nil

        var planStatus: [PlanStatusInfo]? = nil
        if let responsePlanStatus = response.planStatus {
            planStatus = responsePlanStatus.map { status in
                return PlanStatusInfo(
                    statusCode: status.statusCode,
                    status: status.status,
                    planDetails: status.planDetails,
                    serviceTypeCodes: status.serviceTypeCodes
                )
            }
        }
        
        var benefits: [BenefitInfo]? = nil
        if let responseBenefits = response.benefitsInformation {
            benefits = responseBenefits.map { benefit in
                let additionalInfo = benefit.additionalInformation?.compactMap { $0.description }
                
                return BenefitInfo(
                    code: benefit.code,
                    name: benefit.name,
                    coverageLevel: benefit.coverageLevel,
                    serviceTypes: benefit.serviceTypes,
                    planCoverage: benefit.planCoverage,
                    timeQualifier: benefit.timeQualifier,
                    benefitAmount: benefit.benefitAmount,
                    benefitPercent: benefit.benefitPercent,
                    inPlanNetworkIndicator: benefit.inPlanNetworkIndicator,
                    additionalInfo: additionalInfo
                )
            }
        }
        
        return SimplifiedEligibilityData(
            subscriberEntityIdentifier: response.subscriber?.entityIdentifier,
            tradingPartnerServiceId: response.tradingPartnerServiceId,
            payerInfo: payerInfo,
            planInfo: planInfo,
            planDates: planDates,
            planStatus: planStatus,
            benefits: benefits,
            lastChecked: Date()
        )
    }
    
    // MARK: - Helper methods
    func getEligibilityStatus() -> String {
        return planStatus?.first?.status ?? "Unknown"
    }
    
    func getPlanName() -> String? {
        return planStatus?.first?.planDetails
    }
    
    func getPayerPhoneNumber() -> String? {
        return payerInfo?.contacts?.first(where: { $0.communicationMode == "Telephone" })?.communicationNumber
    }
    
    func getPayerWebsite() -> String? {
        return payerInfo?.contacts?.first(where: { $0.communicationMode == "Uniform Resource Locator (URL)" })?.communicationNumber
    }
    
    func getDeductibleAmount() -> String? {
        return benefits?.first(where: { $0.name == "Deductible" })?.benefitAmount
    }

    func getOutOfPocketMaximum() -> String? {
        return benefits?.first(where: { $0.name == "Out of Pocket (Stop Loss)" })?.benefitAmount
    }
    
    func getCoinsurancePercentage() -> String? {
        if let benefitPercent = benefits?.first(where: { $0.name == "Co-Insurance" })?.benefitPercent {
            if let decimal = Double(benefitPercent) {
                return "\(Int(decimal * 100))%"
            }
            return benefitPercent
        }
        return nil
    }
    
    func getCopays() -> [BenefitInfo] {
        return benefits?.filter { $0.name == "Co-Payment" } ?? []
    }
    
    func formatPlanDate(dateString: String?) -> String? {
        guard let dateString = dateString, dateString.count == 8 else { return nil }
        
        let year = dateString.prefix(4)
        let month = dateString.dropFirst(4).prefix(2)
        let day = dateString.dropFirst(6).prefix(2)
        
        return "\(month)/\(day)/\(year)"
    }
    
    func getFormattedPlanBeginDate() -> String? {
        return formatPlanDate(dateString: planDates?.planBegin)
    }

    func getFormattedPlanEndDate() -> String? {
        return formatPlanDate(dateString: planDates?.planEnd)
    }
}
