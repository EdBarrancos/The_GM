""" 
    File: quicksort.py
    Author: Eduardo Barrancos
    Description: QuickSort functions
"""
import  asyncio

async def quicksort(vector: list, left: int, right: int, comparator= lambda a,b: a < b) -> list:
    """ QuickSort a list
            receives the limitations and the comparator function which defaults to less(from smallest to biggest)
            returns the list sorted"""
    if left < right:
        p = await particion(vector, left, right, comparator)
        vector = await quicksort(vector, left, p - 1, comparator)
        vector = await quicksort(vector, p + 1, right, comparator)
        
    return vector


async def particion(vector: list, left: int, right: int, comparator: bool) -> int:
    """ Sort each partition and return the pivot of reference for next partitions """
    pivot = vector[right]
    
    i = left - 1
    
    j = left
    for j in range(left, right):
        if comparator(vector[j], pivot): 
            i += 1
            vector[i], vector[j] = vector[j], vector[i]
    
    if comparator(pivot, vector[i + 1]): vector[i + 1], vector[right] = vector[right], vector[i + 1]
    
    return i + 1