import pytest

def test_file1_method1():
	x=5
	y=6
	assert x+1 == y,"test_file1_method1 1"
	

def test_file1_method2():
	x=1
	y=9
	assert x+8 == y,"test_file1_method2 1"

def test_uppercase():
    assert "loud noises".upper() == "LOUD NOISES"

def test_reversed():
    assert list(reversed([1, 2, 3, 4])) == [4, 3, 2, 1]

def test_some_primes():
    assert 13 in {
        num
        for num in range(1, 50)
        if num != 1 and not any([num % div == 0 for div in range(2, num)])
    }