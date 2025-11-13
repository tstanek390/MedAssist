import SwiftUI

struct ImageDetailView: View {
    let image: MedicalImage
    @Environment(\\.dismiss) var dismiss

    @State private var scale: CGFloat = 1.0
    @State private var lastScale: CGFloat = 1.0

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Image with zoom
                    if let uiImage = UIImage(named: image.imageName) {
                        Image(uiImage: uiImage)
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .scaleEffect(scale)
                            .gesture(
                                MagnificationGesture()
                                    .onChanged { value in
                                        scale = lastScale * value
                                    }
                                    .onEnded { _ in
                                        lastScale = scale
                                    }
                            )
                            .onTapGesture(count: 2) {
                                withAnimation {
                                    if scale > 1.0 {
                                        scale = 1.0
                                        lastScale = 1.0
                                    } else {
                                        scale = 2.0
                                        lastScale = 2.0
                                    }
                                }
                            }
                    } else {
                        ZStack {
                            Rectangle()
                                .fill(Color(.systemGray6))
                                .frame(height: 300)

                            VStack {
                                Image(systemName: "photo")
                                    .font(.system(size: 60))
                                    .foregroundColor(.secondary)
                                Text("Image not found: \\(image.filename)")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                    }

                    // Details
                    VStack(alignment: .leading, spacing: 15) {
                        // Title
                        Text(image.topic)
                            .font(.title2)
                            .fontWeight(.bold)

                        // Badges
                        HStack {
                            Badge(text: image.urgency, color: urgencyColor)
                            Badge(text: image.specialty, color: .blue)
                        }

                        Divider()

                        // Summary
                        if !image.contentSummary.isEmpty {
                            VStack(alignment: .leading, spacing: 5) {
                                Label("Summary", systemImage: "doc.text")
                                    .font(.headline)
                                Text(image.contentSummary)
                                    .font(.body)
                            }

                            Divider()
                        }

                        // Use Case
                        DetailRow(icon: "stethoscope", title: "Use Case", value: image.useCase)

                        // Target Audience
                        DetailRow(icon: "person.2", title: "Target Audience", value: image.targetAudience)

                        Divider()

                        // Key Concepts
                        if !image.keyConcepts.isEmpty {
                            VStack(alignment: .leading, spacing: 10) {
                                Label("Key Concepts", systemImage: "list.bullet")
                                    .font(.headline)

                                FlowLayout(spacing: 8) {
                                    ForEach(image.keyConcepts, id: \\.self) { concept in
                                        Text(concept)
                                            .font(.caption)
                                            .padding(.horizontal, 10)
                                            .padding(.vertical, 5)
                                            .background(Color.purple.opacity(0.1))
                                            .foregroundColor(.purple)
                                            .cornerRadius(8)
                                    }
                                }
                            }
                        }

                        Divider()

                        // Metadata
                        VStack(alignment: .leading, spacing: 5) {
                            Text("Metadata")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text("File: \\(image.filename)")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            Text("Analyzed: \\(formatDate(image.analyzedAt))")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding()
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button {
                            // Share image
                            if let uiImage = UIImage(named: image.imageName) {
                                shareImage(uiImage)
                            }
                        } label: {
                            Label("Share", systemImage: "square.and.arrow.up")
                        }

                        Button {
                            // Reset zoom
                            withAnimation {
                                scale = 1.0
                                lastScale = 1.0
                            }
                        } label: {
                            Label("Reset Zoom", systemImage: "arrow.counterclockwise")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
        }
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

    func formatDate(_ dateString: String) -> String {
        let formatter = ISO8601DateFormatter()
        if let date = formatter.date(from: dateString) {
            let displayFormatter = DateFormatter()
            displayFormatter.dateStyle = .medium
            displayFormatter.timeStyle = .short
            return displayFormatter.string(from: date)
        }
        return dateString
    }

    func shareImage(_ image: UIImage) {
        let activityVC = UIActivityViewController(activityItems: [image], applicationActivities: nil)

        if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let window = windowScene.windows.first,
           let rootViewController = window.rootViewController {
            rootViewController.present(activityVC, animated: true)
        }
    }
}

struct Badge: View {
    let text: String
    let color: Color

    var body: some View {
        Text(text)
            .font(.caption)
            .fontWeight(.semibold)
            .padding(.horizontal, 10)
            .padding(.vertical, 5)
            .background(color.opacity(0.2))
            .foregroundColor(color)
            .cornerRadius(8)
    }
}

struct DetailRow: View {
    let icon: String
    let title: String
    let value: String

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(.purple)
                .frame(width: 24)

            VStack(alignment: .leading, spacing: 3) {
                Text(title)
                    .font(.caption)
                    .foregroundColor(.secondary)
                Text(value)
                    .font(.body)
            }
        }
    }
}

// Flow Layout for key concepts
struct FlowLayout: Layout {
    var spacing: CGFloat

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = arrange(proposal: proposal, subviews: subviews)
        return result.size
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = arrange(proposal: proposal, subviews: subviews)
        for (index, subview) in subviews.enumerated() {
            subview.place(at: CGPoint(x: bounds.minX + result.frames[index].minX,
                                     y: bounds.minY + result.frames[index].minY),
                         proposal: .unspecified)
        }
    }

    private func arrange(proposal: ProposedViewSize, subviews: Subviews) -> (size: CGSize, frames: [CGRect]) {
        var frames: [CGRect] = []
        var x: CGFloat = 0
        var y: CGFloat = 0
        var lineHeight: CGFloat = 0
        let width = proposal.width ?? .infinity

        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)

            if x + size.width > width && x > 0 {
                x = 0
                y += lineHeight + spacing
                lineHeight = 0
            }

            frames.append(CGRect(x: x, y: y, width: size.width, height: size.height))
            lineHeight = max(lineHeight, size.height)
            x += size.width + spacing
        }

        let totalHeight = y + lineHeight
        return (CGSize(width: width, height: totalHeight), frames)
    }
}
