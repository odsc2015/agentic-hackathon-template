//
//  ContentView.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//

import SwiftUI

struct ContentView: View {
    @StateObject var authViewModel = AuthViewModel()
    
    var body: some View {
        Group {
            if authViewModel.isAuthenticated {
                if authViewModel.isOnboardingComplete {
                    HomeView()
                        .environmentObject(authViewModel)
                } else {
                    OnboardingView()
                        .environmentObject(authViewModel)
                }
            } else {
                LoginView()
                    .environmentObject(authViewModel)
            }
        }
    }
}
