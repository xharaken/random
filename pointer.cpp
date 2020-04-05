#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <sys/time.h>

static constexpr int kMetadataShift = 48;
static constexpr int64_t kMetadataMask = 0xffffULL << kMetadataShift;
static constexpr int kOffsetShift = 48;
static constexpr int64_t kOffsetMask = 0xffULL << kOffsetShift;
static constexpr int kGenerationShift = 56;
static constexpr uint64_t kGenerationMask = 0xffULL << kGenerationShift;
static constexpr uint64_t kPointerMask = ~kMetadataMask;

static constexpr char kGenerationValue = 0xff;
static constexpr int kBucketBoundary = 144;

template <typename T>
class RawPtr {
 public:
  RawPtr(T* ptr) : ptr_(ptr) {}
  T* operator->() {
    assert(ptr_);
    return ptr_;
  }
 private:
  T* ptr_;
};

template <typename T>
class CheckedPtr1 {
 public:
  CheckedPtr1(T* ptr) {
    uint64_t bits = reinterpret_cast<uint64_t>(ptr);
    uint64_t generation = ReadGeneration(ptr);
    assert((bits & kMetadataMask) == 0);
    encoded_ptr_ = ((generation << kGenerationShift) | bits);
  }
  T* operator->() {
    uint64_t generation = ReadGeneration(decoded_ptr());
    return reinterpret_cast<T*>((generation << kGenerationShift) ^ encoded_ptr_);
  }
 private:
  char ReadGeneration(T* ptr) const {
    return *(reinterpret_cast<char*>(ptr) - 1);
  }
  T* decoded_ptr() const {
    return reinterpret_cast<T*>(encoded_ptr_ & kPointerMask);
  }
  uint64_t encoded_ptr_;
};

template <typename T>
class CheckedPtr2 {
 public:
  CheckedPtr2(T* ptr) {
    uint64_t bits = reinterpret_cast<uint64_t>(ptr);
    uint64_t generation = ReadGeneration(ptr);
    assert((bits & kMetadataMask) == 0);
    encoded_ptr_ = ((generation << kGenerationShift) | bits);
  }
  T* operator->() {
    uint64_t metadata = encoded_ptr_ >> kMetadataShift;
    uint64_t generation = metadata == 0 ? 0 : ReadGeneration(decoded_ptr());
    return reinterpret_cast<T*>((generation << kGenerationShift) ^ encoded_ptr_);
  }
 private:
  char ReadGeneration(T* ptr) const {
    return *(reinterpret_cast<char*>(ptr) - 1);
  }
  T* decoded_ptr() const {
    return reinterpret_cast<T*>(encoded_ptr_ & kPointerMask);
  }
  uint64_t encoded_ptr_;
};

template <typename T>
class CheckedPtr3 {
 public:
  CheckedPtr3(T* ptr) {
    uint64_t bits = reinterpret_cast<uint64_t>(ptr);
    uintptr_t bucket = (reinterpret_cast<uintptr_t>(ptr) - 1) / kBucketBoundary * kBucketBoundary;
    uint64_t generation = *reinterpret_cast<char*>(bucket);
    assert(generation == kGenerationValue);
    uint64_t offset = reinterpret_cast<uintptr_t>(ptr) - bucket;
    assert((bits & kMetadataMask) == 0);
    encoded_ptr_ = ((generation << kGenerationShift) | (offset << kOffsetShift) | bits);
  }
  T* operator->() {
    uint64_t metadata = encoded_ptr_ >> kMetadataShift;
    uint64_t generation = metadata == 0 ? 0 : ReadGeneration(decoded_ptr());
    // assert(generation == kGenerationValue);
    return reinterpret_cast<T*>(((generation << kGenerationShift) | (encoded_ptr_ & kOffsetMask)) ^ encoded_ptr_);
  }
 private:
  char ReadGeneration(T* ptr) const {
    uint64_t offset = (encoded_ptr_ & kOffsetMask) >> kOffsetShift;
    return *(reinterpret_cast<char*>(ptr) - offset);
  }
  T* decoded_ptr() const {
    return reinterpret_cast<T*>(encoded_ptr_ & kPointerMask);
  }
  uint64_t encoded_ptr_;
};

// Performance test

class TestPointee {
 public:
  TestPointee() : value_(0) {}
  int value() const { return value_; }
  void Increment() { value_++; }
 private:
  int value_;
};

TestPointee* AllocateTestPointee() {
  char* base = static_cast<char*>(calloc(kBucketBoundary + sizeof(TestPointee), sizeof(char)));
  char* object = base + kBucketBoundary;
  *(object - 1) = kGenerationValue;  // generation
  uintptr_t bucket = (reinterpret_cast<uintptr_t>(object) - 1) / kBucketBoundary * kBucketBoundary;
  *(reinterpret_cast<char*>(bucket)) = kGenerationValue;  // generation
  return new (object) TestPointee();
}

double get_time(void)
{
  struct timeval tv;
  gettimeofday(&tv, NULL);
  return tv.tv_sec + tv.tv_usec * 1e-6;
}

void TestRawPtr(int loop) {
  double start = get_time();
  RawPtr<TestPointee> ptr = AllocateTestPointee();
  for (int i = 0; i < loop; i++) {
    if (i % 100000000 == 0) // Prevent the compiler from removing the loop.
      printf("a\b");
    ptr->Increment();
  }
  assert(ptr->value() == loop);
  printf("RawPtr: %.2lf seconds\n", loop, get_time() - start);
}

void TestCheckedPtr1(int loop) {
  double start = get_time();
  CheckedPtr1<TestPointee> ptr = AllocateTestPointee();
  for (int i = 0; i < loop; i++) {
    if (i % 100000000 == 0) // Prevent the compiler from removing the loop.
      printf("a\b");
    ptr->Increment();
  }
  assert(ptr->value() == loop);
  printf("CheckedPtr1: %.2lf seconds\n", loop, get_time() - start);
}

void TestCheckedPtr2(int loop) {
  double start = get_time();
  CheckedPtr2<TestPointee> ptr = AllocateTestPointee();
  for (int i = 0; i < loop; i++) {
    if (i % 100000000 == 0) // Prevent the compiler from removing the loop.
      printf("a\b");
    ptr->Increment();
  }
  assert(ptr->value() == loop);
  printf("CheckedPtr2: %.2lf seconds\n", loop, get_time() - start);
}

void TestCheckedPtr3(int loop) {
  double start = get_time();
  CheckedPtr3<TestPointee> ptr = AllocateTestPointee();
  for (int i = 0; i < loop; i++) {
    if (i % 100000000 == 0) // Prevent the compiler from removing the loop.
      printf("a\b");
    ptr->Increment();
  }
  assert(ptr->value() == loop);
  printf("CheckedPtr3: %.2lf seconds\n", loop, get_time() - start);
}

int main(int argc, char** argv) {
  if (argc < 2) {
    printf("usage: %s loop\n", argv[0]);
    exit(1);
  }
  int loop = atoi(argv[1]);
  TestRawPtr(loop);
  TestCheckedPtr1(loop);
  TestCheckedPtr2(loop);
  TestCheckedPtr3(loop);
  return 0;
}
