//
//  InSureButton.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//

import SwiftUICore
import SwiftUI


// MARK: - Custom Button
struct InSureButton: View {
    var title: String
    var action: () -> Void
    var isSecondary: Bool = false
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.headline)
                .fontWeight(.semibold)
                .foregroundColor(.white)
                .padding()
                .frame(maxWidth: .infinity)
                .background(isSecondary ? Color.accentBlue : Color.primaryBlue)
                .cornerRadius(8)
                .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
        }
    }
}
