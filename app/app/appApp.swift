//
//  appApp.swift
//  app
//
//  Created by Hrigved Khatavkar on 7/25/25.
//

import SwiftUI
import FirebaseCore
import FirebaseAuth
import FirebaseFirestore

// MARK: - AppDelegate for Firebase Setup
class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        FirebaseApp.configure()
        return true
    }
}

// MARK: - App Initialization
@main
struct InSureApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var delegate
    
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

