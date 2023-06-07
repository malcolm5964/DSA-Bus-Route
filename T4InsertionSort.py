def insertion_sort(arr):
    n = len(arr)

    for i in range(1, n):
        key = arr[i]
        j = i - 1

        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key

    return arr


# Example usage
array = [89, 34, 67, 90, 12, 56, 80, 120, 6, 250]
sorted_array = insertion_sort(array)
print(sorted_array)