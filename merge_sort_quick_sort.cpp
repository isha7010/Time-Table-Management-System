#include <iostream>
#include <chrono>
using namespace std;

void merge(int arr[], int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    
    int* L = new int[n1];
    int* R = new int[n2];
    
    for (int i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (int j = 0; j < n2; j++)
        R[j] = arr[mid + 1 + j];
    
    int i = 0, j = 0, k = left;
    
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k++] = L[i++];
        } else {
            arr[k++] = R[j++];
        }
    }
    
    while (i < n1) {
        arr[k++] = L[i++];
    }
    while (j < n2) {
        arr[k++] = R[j++];
    }
    
    delete[] L;
    delete[] R;
}

void mergeSort(int arr[], int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        
        mergeSort(arr, left, mid);
        mergeSort(arr, mid + 1, right);
        
        merge(arr, left, mid, right);
    }
}

int partition(int arr[], int low, int high) {
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

void quickSort(int arr[], int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}

void displayArray(int arr[], int n) {
    cout << "\nSorted array: ";
    for (int i = 0; i < n; i++) {
        cout << arr[i] << " ";
    }
    cout << endl;
}

int main(){
    int n;
    cout << "Enter the no. of element in array: ";
    cin >> n;
    int arr[n];
    
    for (int i = 0; i < n; i++){
        cout << "Enter Number: ";
        cin >> arr[i];
    }
    
    cout << "\nRUNNING BOTH SORTING ALGORITHMS\n";
    
    
    int* mergeSortArr = new int[n];
    int* quickSortArr = new int[n];
    
    for (int i = 0; i < n; i++) {
        mergeSortArr[i] = arr[i];
        quickSortArr[i] = arr[i];
    }
    
   
    auto start1 = chrono::high_resolution_clock::now();
    mergeSort(mergeSortArr, 0, n - 1);
    auto end1 = chrono::high_resolution_clock::now();
    auto duration1 = chrono::duration_cast<chrono::nanoseconds>(end1 - start1);
    
    cout << "\n--- Merge Sort ---";
    displayArray(mergeSortArr, n);
    cout << "Time taken: " << duration1.count() << " nanoseconds" << endl;
    
    // Run Quick Sort
    auto start2 = chrono::high_resolution_clock::now();
    quickSort(quickSortArr, 0, n - 1);
    auto end2 = chrono::high_resolution_clock::now();
    auto duration2 = chrono::duration_cast<chrono::nanoseconds>(end2 - start2);
    
    cout << "\n--- Quick Sort ---";
    displayArray(quickSortArr, n);
    cout << "Time taken: " << duration2.count() << " nanoseconds" << endl;
    
    
    cout << "\n COMPARISON \n";
    if (duration1.count() < duration2.count()) {
        cout << "Merge Sort was faster by " << (duration2.count() - duration1.count()) << " nanoseconds" << endl;
    } else if (duration2.count() < duration1.count()) {
        cout << "Quick Sort was faster by " << (duration1.count() - duration2.count()) << " nanoseconds" << endl;
    } else {
        cout << "Both algorithms took the same time!" << endl;
    }
    
    delete[] mergeSortArr;
    delete[] quickSortArr;
    return 0;
}