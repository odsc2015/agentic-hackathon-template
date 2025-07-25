//
//  HomeView.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//

import SwiftUI


// MARK: - HomeView
struct HomeView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("Welcome to inSure")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.primaryBlue)
                
                Text("You are successfully logged in")
                    .font(.subheadline)
                    .foregroundColor(.textGray)
                
                Spacer()
                
                InSureButton(title: "Sign Out") {
                    authViewModel.signOut()
                }
                .padding(.horizontal)
                .padding(.bottom, 30)
            }
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
    }
}
