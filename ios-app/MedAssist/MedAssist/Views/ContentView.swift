import SwiftUI

struct ContentView: View {
    @StateObject private var dataLoader = DataLoader()
    @StateObject private var searchService = SearchService()
    @StateObject private var claudeService = ClaudeService()

    @State private var selectedImage: MedicalImage?
    @State private var showingAIMode = false

    var filteredImages: [MedicalImage] {
        searchService.filteredImages(from: dataLoader.images)
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                if dataLoader.isLoading {
                    ProgressView("Loading medical images...")
                        .padding()
                } else if let error = dataLoader.error {
                    VStack(spacing: 20) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.system(size: 48))
                            .foregroundColor(.orange)
                        Text("Error Loading Data")
                            .font(.headline)
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                            .padding()
                    }
                    .padding()
                } else {
                    // Search Bar
                    SearchBar(searchText: $searchService.searchText)
                        .padding()

                    // Quick Filters
                    if let taxonomy = dataLoader.taxonomy {
                        FilterBar(
                            specialties: taxonomy.taxonomy.specialties,
                            urgencyLevels: taxonomy.taxonomy.urgencyLevels,
                            selectedSpecialty: $searchService.selectedSpecialty,
                            selectedUrgency: $searchService.selectedUrgency
                        )
                    }

                    // Results Count
                    if !filteredImages.isEmpty {
                        HStack {
                            Text("\\(filteredImages.count) images")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Spacer()
                            if searchService.searchText.isEmpty {
                                Text("Showing all")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .padding(.horizontal)
                    }

                    // Image Grid
                    ScrollView {
                        LazyVGrid(columns: [GridItem(.adaptive(minimum: 150))], spacing: 15) {
                            ForEach(filteredImages) { image in
                                ImageCard(image: image)
                                    .onTapGesture {
                                        selectedImage = image
                                    }
                            }
                        }
                        .padding()
                    }

                    if filteredImages.isEmpty && !searchService.searchText.isEmpty {
                        EmptySearchView()
                    }
                }
            }
            .navigationTitle("MedAssist")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button {
                            searchService.clearFilters()
                        } label: {
                            Label("Clear Filters", systemImage: "xmark.circle")
                        }

                        Button {
                            showingAIMode.toggle()
                        } label: {
                            Label(showingAIMode ? "Disable AI Mode" : "Enable AI Mode", systemImage: "brain")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
            .sheet(item: $selectedImage) { image in
                ImageDetailView(image: image)
            }
            .onAppear {
                dataLoader.loadData()
            }
        }
    }
}

struct SearchBar: View {
    @Binding var searchText: String

    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.secondary)

            TextField("Search medical images...", text: $searchText)
                .textFieldStyle(.plain)

            if !searchText.isEmpty {
                Button {
                    searchText = ""
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(10)
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}

struct FilterBar: View {
    let specialties: [String]
    let urgencyLevels: [String]

    @Binding var selectedSpecialty: String?
    @Binding var selectedUrgency: String?

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                // Urgency Filters
                ForEach(urgencyLevels, id: \\.self) { urgency in
                    FilterChip(
                        title: urgency,
                        isSelected: selectedUrgency == urgency,
                        color: urgencyColor(urgency)
                    ) {
                        if selectedUrgency == urgency {
                            selectedUrgency = nil
                        } else {
                            selectedUrgency = urgency
                        }
                    }
                }

                Divider()
                    .frame(height: 25)

                // Specialty Filters
                ForEach(specialties.prefix(5), id: \\.self) { specialty in
                    FilterChip(
                        title: specialty,
                        isSelected: selectedSpecialty == specialty,
                        color: .blue
                    ) {
                        if selectedSpecialty == specialty {
                            selectedSpecialty = nil
                        } else {
                            selectedSpecialty = specialty
                        }
                    }
                }
            }
            .padding(.horizontal)
        }
    }

    func urgencyColor(_ urgency: String) -> Color {
        switch urgency.lowercased() {
        case "critical": return .red
        case "high": return .orange
        case "medium": return .yellow
        case "low": return .green
        default: return .gray
        }
    }
}

struct FilterChip: View {
    let title: String
    let isSelected: Bool
    let color: Color
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.caption)
                .fontWeight(isSelected ? .semibold : .regular)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(isSelected ? color : Color(.systemGray6))
                .foregroundColor(isSelected ? .white : .primary)
                .cornerRadius(15)
        }
    }
}

struct EmptySearchView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 48))
                .foregroundColor(.secondary)
            Text("No Results Found")
                .font(.headline)
            Text("Try different search terms")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
