import SwiftUI

struct ImageCard: View {
    let image: MedicalImage

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Image
            if let uiImage = UIImage(named: image.imageName) {
                Image(uiImage: uiImage)
                    .resizable()
                    .aspectRatio(contentMode: .fill)
                    .frame(height: 120)
                    .clipped()
                    .cornerRadius(8)
            } else {
                // Placeholder if image not found
                ZStack {
                    Rectangle()
                        .fill(Color(.systemGray5))
                        .frame(height: 120)
                        .cornerRadius(8)

                    VStack {
                        Image(systemName: "photo")
                            .font(.title)
                            .foregroundColor(.secondary)
                        Text("Image not found")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
            }

            // Title
            Text(image.topic)
                .font(.headline)
                .lineLimit(2)
                .minimumScaleFactor(0.8)

            // Urgency Badge
            HStack {
                Text(image.urgency)
                    .font(.caption2)
                    .fontWeight(.semibold)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 3)
                    .background(urgencyColor)
                    .foregroundColor(.white)
                    .cornerRadius(4)

                Spacer()
            }

            // Specialty
            Text(image.specialty)
                .font(.caption)
                .foregroundColor(.secondary)
                .lineLimit(1)
        }
        .padding(10)
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.1), radius: 5, x: 0, y: 2)
    }

    var urgencyColor: Color {
        switch image.urgency.lowercased() {
        case "critical": return .red
        case "high": return .orange
        case "medium": return .yellow
        case "low": return .green
        default: return .gray
        }
    }
}
