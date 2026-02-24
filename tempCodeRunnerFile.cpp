#include <iostream>
#include <vector>
#include <chrono>
using namespace std;
using namespace chrono;

void merge(vector<int>& arr, int left, int mid, int right) {
    vector<int> temp;
    int i = left, j = mid + 1;

    while (i <= mid && j <= right) {
        if (arr[i] <= arr[j])
            temp.push_back(arr[i++]);
        else
            temp.push_back(arr[j++]);
    }

    while (i <= mid) temp.push_back(arr[i++]);
    while (j <= right) temp.push_back(arr[j++]);

    for (int k = 0; k < temp.size(); k++)
        arr[left + k] = temp[k];
}

void mergeSort(vector<int>& arr, int left, int right) {
    if (left < right) {
        int mid = (left + right) / 2;
        mergeSort(arr, left, mid);
        mergeSort(arr, mid + 1, right);
        merge(arr, left, mid, right);
    }
}

int partition(vector<int>& arr, int low, int high) {
    int pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i + 1], arr[high]);
    return i + 1;
}

void quickSort(vector<int>& arr, int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}

int main() {
    int n;
    cout << "Enter number of students: ";
    cin >> n;

    vector<int> rollNumbers(n);
    cout << "Enter roll numbers:\n";
    for (int i = 0; i < n; i++)
        cin >> rollNumbers[i];

    vector<int> arrMerge = rollNumbers;
    vector<int> arrQuick = rollNumbers;

    auto start1 = high_resolution_clock::now();
    mergeSort(arrMerge, 0, n - 1);
    auto end1 = high_resolution_clock::now();
    auto durationMerge = duration_cast<microseconds>(end1 - start1);

    auto start2 = high_resolution_clock::now();
    quickSort(arrQuick, 0, n - 1);
    auto end2 = high_resolution_clock::now();
    auto durationQuick = duration_cast<microseconds>(end2 - start2);

    cout << "\nSorted Roll Numbers (Merge Sort): ";
    for (int x : arrMerge) cout << x << " ";

    cout << "\nSorted Roll Numbers (Quick Sort): ";
    for (int x : arrQuick) cout << x << " ";

    cout << "\n\nExecution Time:\n";
    cout << "Merge Sort: " << durationMerge.count() << " microseconds\n";
    cout << "Quick Sort: " << durationQuick.count() << " microseconds\n";

    return 0;
}
