//
//  UserProfile.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//

import Foundation

struct UserProfile: Codable {
    var firstName: String
    var lastName: String
    var insuranceProvider: String?
    var memberID: String?
    var dateOfBirth: Date?
    var eligibilityStatus: String?
    var lastEligibilityCheck: Date?
    
    var formattedDateOfBirth: String? {
        guard let dob = dateOfBirth else { return nil }
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        return formatter.string(from: dob)
    }
    
    var formattedLastEligibilityCheck: String? {
        guard let date = lastEligibilityCheck else { return nil }
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}
