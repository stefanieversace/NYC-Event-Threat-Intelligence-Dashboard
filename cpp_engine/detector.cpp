#include <iostream>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <vector>

using namespace std;

struct Alert {
    string ip;
    int attempts;
    string severity;
    string mitre;
};

string getSeverity(int attempts) {
    if (attempts >= 10) return "HIGH";
    if (attempts >= 5) return "MEDIUM";
    return "LOW";
}

int main() {
    ifstream file("logs.txt");
    string line;

    if (!file.is_open()) {
        cerr << "Error: Could not open logs.txt\n";
        return 1;
    }

    unordered_map<string, int> failedAttempts;
    vector<Alert> alerts;

    // 🔍 Read and process logs
    while (getline(file, line)) {
        stringstream ss(line);
        string ip, status;

        ss >> ip >> status;

        if (status == "FAIL") {
            failedAttempts[ip]++;
        }
    }

    file.close();

    // 🚨 Generate alerts
    for (auto& pair : failedAttempts) {
        int attempts = pair.second;

        if (attempts >= 5) {
            Alert alert;
            alert.ip = pair.first;
            alert.attempts = attempts;
            alert.severity = getSeverity(attempts);
            alert.mitre = "T1110 - Brute Force";

            alerts.push_back(alert);
        }
    }

    // 
    ofstream out("../data/alerts.json");

    if (!out.is_open()) {
        cerr << "Error: Could not write to alerts.json\n";
        return 1;
    }

    out << "[\n";

    for (size_t i = 0; i < alerts.size(); i++) {
        out << "  {\n";
        out << "    \"ip\": \"" << alerts[i].ip << "\",\n";
        out << "    \"attempts\": " << alerts[i].attempts << ",\n";
        out << "    \"severity\": \"" << alerts[i].severity << "\",\n";
        out << "    \"mitre\": \"" << alerts[i].mitre << "\"\n";
        out << "  }";

        if (i != alerts.size() - 1) out << ",";
        out << "\n";
    }

    out << "]\n";

    out.close();

    cout << "Detection complete. Alerts written to data/alerts.json\n";

    return 0;
}
