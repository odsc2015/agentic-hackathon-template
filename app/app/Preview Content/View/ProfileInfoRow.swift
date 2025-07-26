//
//  ProfileInfoRow.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//

import SwiftUICore

// Helper view for profile information display
struct ProfileInfoRow: View {
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
        .padding(.vertical, 4)
    }
}
