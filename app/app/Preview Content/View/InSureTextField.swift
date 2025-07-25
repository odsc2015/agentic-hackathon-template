import SwiftUI

// MARK: - Keyboard Dismissal Extension
extension View {
    func dismissKeyboard() -> some View {
        return self.onTapGesture {
            UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
        }
    }
}

// MARK: - Custom TextFields
struct InSureTextField: View {
    var placeholder: String
    @Binding var text: String
    var isSecure: Bool = false
    var keyboardType: UIKeyboardType = .default
    @State private var isPasswordVisible: Bool = false
    
    var body: some View {
        HStack {
            ZStack(alignment: .leading) {
                // Custom placeholder in gray
                if text.isEmpty {
                    Text(placeholder)
                        .foregroundColor(.gray)
                        .padding(.leading, 2)
                }
                
                if isSecure {
                    if isPasswordVisible {
                        TextField("", text: $text)
                            .keyboardType(keyboardType)
                    } else {
                        SecureField("", text: $text)
                            .keyboardType(keyboardType)
                    }
                } else {
                    TextField("", text: $text)
                        .keyboardType(keyboardType)
                }
            }
            .foregroundColor(.black)
            
            if isSecure {
                Button(action: {
                    isPasswordVisible.toggle()
                }) {
                    Image(systemName: isPasswordVisible ? "eye.slash.fill" : "eye.fill")
                        .foregroundColor(.gray)
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(8)
        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
        .autocapitalization(.none)
    }
}

// Preview provider for SwiftUI Canvas
struct InSureTextField_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 20) {
            InSureTextField(placeholder: "Email", text: .constant(""))
            InSureTextField(placeholder: "Password", text: .constant(""), isSecure: true)
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .previewLayout(.sizeThatFits)
    }
}
