---
title: "[Core] BVH 분석"
author: KurtJang
tags:
  - Blog
  - "#Programming"
  - SteamAudio
  - CPP
date: 2026-06-22
draft: "False"
description: "[SteamAudio] BVH 분석 (core module)"
---

---

# 1. Introduction

## BVH (Bounding Volume Hierarchy)

![[core_bvh-1782879266800.webp|650x294]]

- 트리구조 (N개의 삼각형, 2N-1개의 노드)

> [!info]  예제
> 만약 총알이 어떤 벽이나 메시에 맞았는지 판단해야 한다면?
> 그리고 맵에 100만개의 삼각형이 있다면?
>
> 100만번의 충돌검사는 엄청난 비효율
> 따라서 <font color="#b3f594">"큰 상자안에 작은 상자들을 계층적으로 집어넣는 방법"</font>이 바로 BVH
> 
> 원리
>  - 먼저 전체 맵을 감싸는 거대한 상자(Root)를 만든다
>  - 그 상자를 반씩 쪼개 나아가며 작은 상자들을 만든다
>  - 맨 마지막 (leaf) 안에는 실제 물체 (삼각형)이 들어있게 된다
> <br>
> 
>효과
> - 광선이 가장 큰 상자를 통과하지 못했다면 
>   그안의 100만개 삼각형은 검사도 안하고 통째로 건너 뛸 수 있다
> - 이 덕분에 성능이 O(N)에서 O(logN)으로 획기적으로 줄어듬
> 
> 


---
# 2. 구성 요소

<strong style="color:#b3f594">1. Box</strong>

- min, max로 표현
- Steam Audio 의 경우 SIMD를 위해 vector4를 사용하며 padding 4byte의 경우
  메타데이터를 끼워넣어서 메모리 효율화를 한다
- 마지막 bit
	- 3이면 = internal node
	- 0~2면 = leaf node의 axis (0 = x, y = 1, z = 2)

![[core_bvh-1782879327715.webp]]

<strong style="color:#b3f594">2. BVHNode</strong>

- internal node일 경우 
	- 알맹이(삼각형)이 없고 자식 노드를 가리키는 포인터/오프셋역할
- leaf node일 경우
	- 트리 구조의 맨끝에 존재하며, 실제 삼각형의 인덱스 번호를 가지고 있는 상자

---
# 3. 예제 코드

``` cpp
#inlcude <iostream>
#include <vector

struct SimpleBox{
    float minX, minY;
	
	bool intersect(float rayX) const
	{
	    return ray x >= minX && rayX <= maxX;
	}
}

struct SimpleBVHNode{
    SimpleBox box;
    bool isLeaf;
	int triangleIndex;   //leaf node일때만 유효(실제 삼각형 번호)
    int leftChild, rightChild; // internal node일때만 유효(자식 위치)
}

void intersectRay(const std::vector<SimpleBVHNode>& bvh, 
                  int nodeIdx, 
                  float rayX)
{
    //1. 현재 상자에 부딪히지도 않았따면 하위 상자들을 볼 필요 없음
    if (!node.box.intersect(rayX)) return;
    
    //2. 만약 leaf node라면 드디어 실제 trinagle과 충돌을 확인
    if (node.isLeaf)
    {
        std::cout << "충돌 노드" << node.triangleIndex << "번 삼각형";
        return;
    }
    
    //3. internal node라면 자식 상자들을 내부적으로 타고 내려감
    //recursive
    intersectRay(bvh, node.leftChild, reyX);
    intersectRay(bvh, node.rightChild, rayX);
}

int main()
{
    SimpleBVHNode rootNode = SimpleBVHNode();
    root.box = SimlpeBox(0.0f, 10.0f);
    root.isLeaf = false;
    root.triangleIndex = -1;
    root.leftChild = 1;
    root.rightChild = 2;
    
    //leaf node (left)
    SimpleBVHNode lNode = SimpleBVHNode();
    lNode.box = SimpleBox (0.0f, 5.0f);
    lNode.isLeaf = true;
    lNode.triangleIndex = 99;
    lNode.leftChild = -1;
    lNode.rightChild = -1;
    
    //leaf node (right)
    SimpleBvhNode rNode = SimpleBVHNode();
    rNode.box = SimpleBox(0.0f, 10.0f);
    rNode.isLeaf = true;
    rNode.triangleIndex = 100;
    rNode.leftChild = -1;
    rNode.rightChild = -1;
    
    std::vector<SimpleBVHNode> dummyBVH;
    dummyBVH.push_back(rootNode);
    dummyBVH.push_back(lNode);
    dummyBVH.push_back(rNode);
    
    float fakeRayPosition = 3.0f;
    std::cout << "location = " << fakeRayPostiion << "ray ges";
    intersectRay(dummyBVH, 0, fakeRayPosition);
    
    return 0;
}


```

---

# 3. 실전 코드

``` cpp
// bvh.h

#include "box.h"
#include "float4.h"
#include "mesh.h"
#include "platform.h"
#include "ray.h"


namespace ipl {

// ----------------------------------------
// BVHNode
// ----------------------------------------

// A node in a BVH. All the information required to represent a node,
// including information and children, and BVH splitting planes, is
// compactly stored in an array of 32-byte Box objects. Each Box represents
// a node and its bounding box. The remaining information is encoded in the
// first 4 bytes of padding, as follows:
//
//  Leaf nodes:
//      30 bits     triangle index
//       2 bits     the constant value 3
//
//  Internal nodes:
//      30 bits     offset from the current node to its left child
//       2 bits     split axis (0 = x, 1 = y, 2 = z).
class BVHNode
{
public:
    bool isLeaf() const
    {
        return (getSplitAxis() == 3);
    }

    int32_t getSplitAxis() const
    {
        return (data() & 3);
    }

    int32_t getTriangleIndex() const
    {
        return (data() >> 2);
    }

    void setTriangleIndex(int32_t triangleIndex)
    {
        data() = (triangleIndex << 2) | 3;
    }

    void setInternalNodeData(int32_t childOffset,
                             int32_t splitAxis)
    {
        data() = (childOffset << 2) | splitAxis;
    }

    BVHNode& leftChild()
    {
        return this[data() >> 2];
    }

    BVHNode& rightChild()
    {
        return this[(data() >> 2) + 1];
    }

    Box& boundingBox()
    {
        return mBoundingBox;
    }

    const Box& boundingBox() const
    {
        return mBoundingBox;
    }

private:
    int32_t& data()
    {
        return reinterpret_cast<int32_t*>(&mBoundingBox.minCoordinates)[3];
    }

    const int32_t& data() const
    {
        return reinterpret_cast<const int32_t*>(&mBoundingBox.minCoordinates)[3];
    }

    Box mBoundingBox;
};


// ---------------------------------------
// GrowableBox
// ---------------------------------------
// Represents a Box that can be efficiently grown to contain other primitives, using SIMD instructions.
class GrowableBox
{
public:
    GrowableBox()
    {
        reset();
    }

    void reset()
    {
        mMinCoordinates = float4::set1(std::numeric_limits<float>::max());
        mMaxCoordinates = float4::set1(-std::numeric_limits<float>::max());
    }

    void growToContain(const Vector3f& point)
    {
        auto pointCoordinates = float4::load(point.elements);
        mMinCoordinates = float4::min(mMinCoordinates, pointCoordinates);
        mMaxCoordinates = float4::max(mMaxCoordinates, pointCoordinates);
    }

    void growToContain(const Mesh& mesh,
                       int triangleIndex)
    {
        growToContain(mesh.triangleVertex(triangleIndex, 0));
        growToContain(mesh.triangleVertex(triangleIndex, 1));
        growToContain(mesh.triangleVertex(triangleIndex, 2));
    }

    void growToContain(const GrowableBox& box)
    {
        mMinCoordinates = float4::min(mMinCoordinates, box.mMinCoordinates);
        mMaxCoordinates = float4::max(mMaxCoordinates, box.mMaxCoordinates);
    }

    void load(const Box& box)
    {
        mMinCoordinates = float4::load(box.minCoordinates.elements);
        mMaxCoordinates = float4::load(box.maxCoordinates.elements);
    }

    void store(Box& box) const
    {
        float4::store(box.minCoordinates.elements, mMinCoordinates);
        float4::store(box.maxCoordinates.elements, mMaxCoordinates);
    }

    float getSurfaceArea() const
    {
        auto extents = float4::sub(mMaxCoordinates, mMinCoordinates);

#if (defined(IPL_CPU_ARMV7) || defined(IPL_CPU_ARM64))
        alignas(Memory::kDefaultAlignment)float extentsArray[4];
        float4::store(extentsArray, extents);
        return 2.0f * (extentsArray[0] * extentsArray[1] + extentsArray[1] * extentsArray[2] + extentsArray[2] * extentsArray[0]);
#else
        // The box extents are stored in an SSE register as [dx dy dz ?]
        // We first shuffle this register and multiply the result, to
        // obtain [dx dy dz ?] * [dy dz dx ?] = [dxdy dydz dzdx ?].
        extents = float4::mul(extents, _mm_shuffle_ps(extents, extents, _MM_SHUFFLE(3, 0, 2, 1)));

        // Now we shuffle this product two times, and add the resulting three
        // terms together, and multiply the result by 2:
        // 2 * ([dxdy dydz dzdx ?] + [dydz dzdx dxdy ?] + [dzdx dxdy dydz ?])
        // = [A A A ?], where A is the surface area.
        extents = float4::add(extents, float4::add(_mm_shuffle_ps(extents, extents, _MM_SHUFFLE(3, 1, 0, 2)), _mm_shuffle_ps(extents, extents, _MM_SHUFFLE(3, 0, 2, 1))));
        extents = float4::mul(extents, float4::set1(2.0f));

        // Save the result.
        alignas(Memory::kDefaultAlignment) float surfaceArea[4];
        float4::store(surfaceArea, extents);
        return surfaceArea[0];
#endif
    }

private:
    float4_t mMinCoordinates;
    float4_t mMaxCoordinates;
};


// ----------------------------------------
// CentroidCoordinate
// ----------------------------------------
// Represents a single coordinate of a leaf node centroid.
struct CentroidCoordinate
{
    float coordinate;
    int32_t leafIndex;
};


// -----------------------------------------
// Split
// -----------------------------------------

// Represents a split of an array of leaf nodes into two sub-arrays.
struct Split
{
    int32_t index;
    int32_t axis;
};


// ---------------------------------------
// BVH
// ---------------------------------------
// A Bounding Volume Hierarchy (BVH), consisting of axis-aligned bounding boxes (AABBs).
class BVH
{
public:
    BVH(const Mesh& mesh,
        ProgressCallback progressCallback = nullptr,
        void* userData = nullptr);

    int32_t numNodes() const
    {
        return static_cast<int32_t>(mNodes.size(0));
    }

    BVHNode& node(int32_t index)
    {
        return mNodes[index];
    }

    const BVHNode& node(int32_t index) const
    {
        return mNodes[index];
    }

    // Calculates the first intersection between a ray and any triangle in the BVH.
    Hit intersect(const Ray& ray,
                  const Mesh& mesh,
                  float minDistance,
                  float maxDistance) const;

    // Checks whether a ray is occluded by any triangle in the BVH.
    bool isOccluded(const Ray& ray,
                    const Mesh& mesh,
                    float minDistance,
                    float maxDistance) const;

    // Checks whether the ray between two points is occluded by any
    // triangle in the BVH. This function does not apply any tolerances
    // at either end point, so if either start or end is close to a
    // surface (as is likely to occur for reflected or shadow rays), the
    // ray may intersect with the reflecting surface. Care must be taken in
    // such cases to add an appropriate tolerance to the start point.
    bool isOccluded(const Vector3f& start,
                    const Vector3f& end,
                    const Mesh& mesh) const;

    // Returns true if the given box contains any geometry.
    bool intersect(const Box& box,
                   const Mesh& mesh) const;

    // Returns true if the given boxes intersect.
    static bool boxIntersectsBox(const Box& box1,
                                 const Box& box2);

private:
    // Maximum recursion depth during BVH construction.
    static const int kConstructionStackDepth = 128; 
    // Maximum recursion depth during BVH traversal.
    static const int kTraversalStackDepth = 128; 

    Array<BVHNode> mNodes; // The nodes of the BVH.

    // Builds a BVH using the triangles in a Mesh.
    void build(const Mesh& mesh,
               ProgressCallback progressCallback,
               void* userData);

    // Calculates the best split between the triangles in an internal node.
    Split bestSplit(GrowableBox* leafNodes,
                    int32_t* leafIndices,
                    CentroidCoordinate* const* centroids,
                    float* surfaceAreas,
                    const Box& boundingBox,
                    int32_t startIndex,
                    int32_t endIndex);

    // Uses the object median split approach for splitting an internal node
    //.This is worse than an SAH split, but is useful in certain degenerate  
    // cases. The set of leaves is split at the median leaf index: 
    // roughly half of the leaves end up in the left child, 
    // the rest in the right child.
    Split medianSplit(GrowableBox* leafNodes,
                      int32_t* leafIndices,
                      CentroidCoordinate* const* centroids,
                      const Box& boundingBox,
                      int32_t startIndex,
                      int32_t endIndex);

    // Uses the Surface Area Heuristic (SAH) split approach for splitting
    // an internal node. Results in better ray tracing performance than
    // the median split approach, but does not work in certain degenerate
    // cases.
    Split sahSplit(GrowableBox* leafNodes,
                   int32_t* leafIndices,
                   CentroidCoordinate* const* centroids,
                   float* surfaceAreas,
                   const Box& boundingBox,
                   int32_t startIndex,
                   int32_t endIndex);

    // Evaluates the SAH cost function.
    float sahCost(float leftChildSurfaceArea,
                  int32_t numLeftChildren,
                  float rightChildSurfaceArea,
                  int32_t numRightChildren,
                  float parentSurfaceArea) const;

    // Returns true if the given triangle intersects the given box.
    static bool boxIntersectsTriangle(const Box& box,
                                      const Mesh& mesh,
                                      int32_t triangleIndex);
};

}

```



``` cpp

//bvh.cpp

// Copyright 2017-2023 Valve Corporation.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

#include "bvh.h"

#include "stack.h"

namespace ipl {

// ----------------------------------------
// ConstructionTask
// ----------------------------------------
// Represents a unit of work during BVH construction.
struct ConstructionTask
{
    int32_t outputNodeIndex;
    int32_t startIndex;
    int32_t endIndex;
    int32_t leftChildIndex;
};


// ----------------------------------------
// TraversalTask
// ----------------------------------------
// Represents a unit of work during BVH traversal.
struct TraversalTask
{
    int32_t nodeIndex;
    float tMin;
    float tMax;
};


// ----------------------------------------
// BVH
// ----------------------------------------
BVH::BVH(const Mesh& mesh,
         ProgressCallback progressCallback,
         void* userData)
    : mNodes(2 * mesh.numTriangles() - 1)
{
    build(mesh, progressCallback, userData);
}

void BVH::build(const Mesh& mesh,
                ProgressCallback progressCallback,
                void* userData)
{
    // The leafIndices array stores the indices of the mesh's triangles, in
    // left-to-right order as they appear in the final constructed BVH. When
    // construction begins, these are simply initialized in sorted order.
    // As construction proceeds, subarrays of this array will be permuted
    // based on how internal nodes are split.
    Array<int32_t> leafIndices(mesh.numTriangles());
    for (auto i = 0U; i < leafIndices.size(0); ++i)
    {
        leafIndices[i] = i;
    }
    
    // The leafNodes array stores the bounding boxes of each mesh triangle.
    Array<GrowableBox> leafNodes(mesh.numTriangles());
    for (auto i = 0; i < mesh.numTriangles(); ++i)
    {
        leafNodes[i].reset();
        leafNodes[i].growToContain(mesh, i);
        /*
        * mesh triangle의 꼭지점을 모두 감싸는 AABB bounding box 생성
        */
    }

    // The leafBoxCenters array stores the centers of the bounding boxes of
    // 1each mesh triangle.
    Array<Vector3f> leafBoxCenters(mesh.numTriangles());
    for (auto i = 0; i < mesh.numTriangles(); ++i)
    {
        alignas(Memory::kDefaultAlignment) Box box;
        leafNodes[i].store(box);
        leafBoxCenters[i] = box.center();
        /*
        * Box의 정 중앙점 계산
        */
    }
    
    /*
    왜 Boudninb box와 centroid를 계산하는가?
     - 삼각형을 쪼갤때 "삼각형의 중심점" 이 어디에 치우쳐 있는지를
       기준으로 정렬하기 때문
     - 매번 계산하면 느리기 때문에 미리 구해서 caching
    */
    
    // The centroids arrays are temporary storage used for 
    // sorting nodes by centroid coordinates.
    Array<CentroidCoordinate, 2> centroids(3, mesh.numTriangles());

    // The surfaceAreas array is temporary storage used 
    // for calculating surface areas of internal nodes.
    Array<float> surfaceAreas(mesh.numTriangles());

    // We begin by building the root node at index 0. 
    // It contains all the triangles in
    // the entire leafIndices array.
    Stack<ConstructionTask, kConstructionStackDepth> stack;
    ConstructionTask task = ConstructionTask{
	    0, 
 	    0, 
	    static_cast<int32_t>(leafNodes.size(0)) - 1, 1 };
	/*
	 왜 resursive 대신 stack을 썼을까?
	 
	 일반전 방식
	  - build (left), build (right)의 resurvie 방식
	 Steam Audio
	  - Stack 자료 구조 + while loop
	    
	  왜?
	   - 게임이나 오디오 엔진 환경에서 mesh의 triangle이 수백만개
	     일 경우 recursive는 stack overflow 발생
	   - 안전 버퍼(kConstructionStackDepth = 128)을 가진 stack 객체를
	     생성해 안정성과 속도를 모두 챙긴 케이스
	*/

    // At each step of construction, we're processing a node containing
    // all the triangles in leafIndices[startIndex] to 
    // leafIndices[endIndex],
    // inclusive.
    while (true)
    {
        auto oneLeafLeft = (task.startIndex == task.endIndex);

        if (oneLeafLeft)
        {
	        //1. 최종 결정됨 box 를 BVH 저장
            leafNodes[leafIndices[task.startIndex]].store
            (
               mNodes[task.outputNodeIndex].boundingBox()
            );
            
            //2. "몇번 삼각형" 을 가지고 있는지 기록
            mNodes[task.outputNodeIndex].setTriangleIndex
            (
               leafIndices[task.startIndex]
            );

            if (stack.isEmpty())
                break;
                
            //남아있는 box의 쪼개기 작업 가져오기
            task = stack.pop();
            
            /*
            만약 상자를쪼개다 삼각형이 딱1개 남았다면
            해당 node를 leaf node로 선언하고 index 매치 이후 끝낸다
            */
        }
        else //삼각형이 여러개 남았을때
        {
             /*
             1. 현재 범위 내에 있는 삼각형들 모두 감싸는 boudning box를 구한다
             */
        
            // For internal nodes, we first construct a bounding box that
            // encloses all its triangles.
            GrowableBox boundingBox;
            for (auto i = task.startIndex; i <= task.endIndex; ++i)
            {
                boundingBox.growToContain(leafNodes[leafIndices[i]]);
            }

            boundingBox.store(mNodes[task.outputNodeIndex].boundingBox());
            

            /*
             2. x,y,z axis별 삼각형 중심점들을 임시 버퍼에 채워 넣는다
          
             ** 어디를 잘라야 상자가 이쁜지 모르니 x,y,z 줄을 세운다**
             
             centroid[0][i] = i번째 삼각형 x의 좌표들만 모음
             centroid[1][i] = i번째 삼각형 y의 좌표들만 모음
             centroid[2][i] = i번째 삼각형 z의 좌표들만 모음
             
             ** 알맹이 보호 **
             centroids를 바꾸면서 leftIndex또한 해당 삼각형으로 묶어서 저장
             
             ** 만약 이런 행동을 하지 않으면? **
             만약 임시 정렬판을 안만들고 원본 배열인 leafIndiecs나 
             leafBoxCenters를 x축 기준으로 정렬해버렸다고 가정
              - 컴퓨터가 열심히 계산하다가 'x축이 별로야 y축으로 계산 다시'
                라고 한다면 이미 데이터가 x축 순서로 뒤죽박죽 섞여서
                원상복구가 불가능함
              
              Valve의 해결책
               - 원본 leafIndices, leafBoxCenters는 그대로 둔다
               - ceontrids라는 별도의 복사본 x,y,z를 만든다
               - bestSplit 함수에게 이 정렬판 3개를 던져준다
               - bestSplit는 임시 정렬판 안에서 마음껏 데이터를 정렬하고 
                 뒤흔들며 SAH비용을 계산
               - 최종적으로 'x축의 5번째 위치를 자르는게 비용이 제일 적어'
                 라고 결정이 나면 그제야 원본 배열을 딱 한번만
                 최종 결정상태로 업데이트 한다
            */

            // For each axis, centroids[axis][i] contains the coordinate of
            // the centroid of leaf node leafIndices[i].
            for (auto i = task.startIndex; i <= task.endIndex; ++i)
            {
                centroids[0][i].coordinate = 
                leafBoxCenters[leafIndices[i]].x();
                centroids[1][i].coordinate = 
                leafBoxCenters[leafIndices[i]].y();
                centroids[2][i].coordinate = 
                leafBoxCenters[leafIndices[i]].z();
                
                centroids[0][i].leafIndex = leafIndices[i];
                centroids[1][i].leafIndex = leafIndices[i];
                centroids[2][i].leafIndex = leafIndices[i];
            }
            
            /*
             3. [최적의 하이라이트] 최적의 분할 지점을 찾고 구조를 결정
            */

            // Split the node into left and right children.
            auto split = bestSplit(leafNodes.data(), 
                leafIndices.data(), 
                centroids.data(), 
                surfaceAreas.data(),
                mNodes[task.outputNodeIndex].boundingBox(), 
                task.startIndex, 
                task.endIndex);
            
            // left child node가 원본 배열에서 얼마나 떨어졌는지
            // offset / axis축 (x= 0, y = 1, z = 2) 저장
            // bestSplit이후에 axis 와 index가 나온다
            mNodes[task.outputNodeIndex].setInternalNodeData(
               task.leftChildIndex - task.outputNodeIndex, 
               split.axis);
               
               
            /*
            Index 설계와 연산 예시
               
            배열 한개 mNodes에 모든 이진트리 노드를 촘촘하게 채워넣기 위해 
            독특한 index 규칙을 사용
            
            eg) 삼각형 4ea, root node를 처리하는 사황
            
            task.outputIndex = 0 (root)
            task.startIndex = 0
            task.endIndex = 3 (삼각형 4개 - 0 ~ 3)
            task.leftChildIndex = 1 (자식 노드가 배치될 시작점)
            
            알고리즘(bestSplit) 연산을 해보니 
            왼쪽 상자1개, 오른쪽 상자 3개로 쪼개는게 최고라는 결론
            
            split.index = 1
            (왼쪽에 1개 배치ㅗ디므로 커드라인 인덱스는 1)
            
            [1] right child의 task (stak.push)
            
            outputNodeIndex = task.leftChildIndex + 1;  //2;
            startIndex = task.startIndex + split.index; //1
            //0 + 1 = 1
            endIndex = task.endIndex; // 3
            leftChildIndex = (task.leftChildIndex + 2) * splitIndex; //3
            //1 + 2 * 1 = 3
            
            결론 - '나중에 2번 노드를 만들건데 여기엔 1~3번 삼각형이 들어가고
             이녀석의 자식들은 3번 노드로부터 배치해라'가 스택에 저장
            
            [2] 곧바로 처리할 left child node task (task 교체)
            
            outputNodeIndex = task.leftChildIndex; //1
            startIndex = task.startIndex; //0
            endIndex = task.startIndex + split.index; //0 + 1 -1 = 0
            leftChildIndex = task.leftChildIndex + 2 //1 + 2 = 3
        
            결론 - '다음 루프로 넘어가면서 1번 노드를 만들고 여기엔 0번 삼각형
                   1개만 들어간다'
            
            [3] 다음 루프의 실행
            다음 루프를 시작하자마자 startIndex == endIndex가 같으므로
            이 1번 노드는 "곧바로 리프 노드로 확정" 되어 저장되고 끝난다
            
            요약
            이 코드는 거대한 메모리 배열 하나를 선언해두고 '좌우 상자를 쪼개
            가면서 스택을 이용해 빈틈없이 노드들을 다닥다닥 채워넣는 구조'
            포인터를 쓰지 않고 인덱스 오프셋 정수 연산만 사용하기 떄문에
            cpu 캐시 효율이 극대화 되어 오디오/그래픽 연산속도가 압도적으로 빠르다
            */

		
		    //4. right child node가 해야 할일을 stack에 보관
            // Push the right child onto the stack. 
            // Set the current task to the left child, and continue.
            stack.push(ConstructionTask{task.leftChildIndex + 1,
                task.startIndex + split.index, 
                task.endIndex, 
                task.leftChildIndex + 2 * split.index});
                
            //5. 현재 task를 left child node task로 교체하고
            // continue를 통해 다음 loop 로 진입
            task = ConstructionTask{ task.leftChildIndex, 
               task.startIndex, 
               task.startIndex + split.index - 1, 
               task.leftChildIndex + 2 };
               
            continue;
        }
    }

    if (progressCallback)
    {
        progressCallback(1.0f, userData);
    }
}

/*
  sah를 먼저 시도하고 도형이 비정상적으로 겹치거나 찌그러져서 SAH 연산이
  실패한다면 (axis == -1), medianSplit(중앙분할) 진행
*/
Split BVH::bestSplit(GrowableBox* leafNodes,
                     int32_t* leafIndices,
                     CentroidCoordinate* const* centroids,
                     float* surfaceAreas,
                     const Box& boundingBox,
                     int32_t startIndex,
                     int32_t endIndex)
{
	

    // When finding the best split of an internal node, we first try the SAH
    // approach. If that fails (usually due to degenerate nodes), we use the
    // median split approach.
    auto split = sahSplit(leafNodes, 
                          leafIndices, 
                          centroids, 
                          surfaceAreas, 
                          boundingBox, 
                          startIndex, 
                          endIndex);
                          
    if (split.axis == -1)
        split = medianSplit(leafNodes, 
                           leafIndices, 
                           centroids, 
                           boundingBox, 
                           startIndex, 
                           endIndex);

    return split;
}

/*
 medainSplit
 삼각형들을 정렬한 뒤, 효율과 상관없이 무조건 개수 기준으로 정확히
 50:50 반을 쪼개는 방식
*/
Split BVH::medianSplit(GrowableBox* leafNodes,
                       int32_t* leafIndices,
                       CentroidCoordinate* const* centroids,
                       const Box& boundingBox,
                       int32_t startIndex,
                       int32_t endIndex)
{
    //가장 긴 axis 선택
    auto splitAxis = boundingBox.extents().indexOfMaxComponent();
    auto splitIndex = (endIndex - startIndex + 1) / 2;

    for (auto i = startIndex; i <= endIndex; ++i)
    {
        //원본 인덱스 복사사
        leafIndices[i] = centroids[splitAxis][i].leafIndex;
    }

    return Split{ splitIndex, static_cast<int32_t>(splitAxis) };
}

/*
 SAH (Surface Area Heuristic) 
 BVH에서 ray를 사용할때 가장 효율적인 BVH 구축을 위한 최적화 방식
 'ray가 스쳐 지나갈 확률은 box의 표면적에 비례한다' 라는
 화귤기하학적 법칙을 기반으로 비용 계산
 
 x,y,z 세축을 돌며 split 가능한 지점의 비용을 전수 조사
 (전수 조사 이지만 two pass 구조로 잘 짜여져 있다)
*/
Split BVH::sahSplit(GrowableBox* leafNodes,
                    int32_t* leafIndices,
                    CentroidCoordinate* const* centroids,
                    float* surfaceAreas,
                    const Box& boundingBox,
                    int32_t startIndex,
                    int32_t endIndex)
{
    alignas(Memory::kDefaultAlignment) GrowableBox parentBox;
    parentBox.load(boundingBox);
    auto parentSurfaceArea = parentBox.getSurfaceArea();
    auto bestCost = std::numeric_limits<float>::max();
    auto split = Split{ -1, -1 };

    for (auto axis = 0; axis < 3; ++axis)
    {
        auto bestBalanceCost = std::numeric_limits<int>::max();

        auto centroidsForAxis = centroids[axis];
        
        //step 1. axis별 정렬 및 왼쪽 상자들의 면적 예치(1st pass)
        
        //1. 임시 정렬파능ㄹ 좌표 순서대로 줄 세운다
        // Sort the leaves by centroid coordinates.
        std::sort(
        &centroidsForAxis[startIndex], 
        &centroidsForAxis[endIndex + 1], 
        [](const CentroidCoordinate& a, const CentroidCoordinate& b)
        {
            return (a.coordinate < b.coordinate);
        });
        
        //2. 왼쪽에서부터 칸을 하나씩 옮겨가며 누적 상자 면적을 미리 계산
        // Consider all possible splits, 
        //and evaluate the surface area of the left child for each case.
        GrowableBox leftChildBox;
        leftChildBox.reset();
        for (auto index = startIndex; index < endIndex; ++index)
        {
            leftChildBox.growToContain(
            leafNodes[centroidsForAxis[index].leafIndex]);
            
            surfaceAreas[index] = leftChildBox.getSurfaceArea();
        }
        
        
        /*step 2. 오른쪽에서 오며 최종 비용 계산 및 비교 (2nd pass)
          
          오른쪽 endIndex에서 거꾸로 걸어오며 오른쪽 상자 그룹(rightchildbox)의
          크기를 키운다
          동시에 아까 step1에서 정방향으로 구해놓은 왼쪽 상자의 면적을 매칭시켜
          sahCost 함수를 태운다
          이방식으로 단 2번의 루프판에 모든 지점의 좌/우 박스 조합 비용을
          얻어내는 뛰어난 최적화 기법
          
          
        */
    
        // Consider all possible splits, and evaluate 
        // the surface area of the right child for each case. 
        // Also evaluate the SAH cost function and find the best split.
        GrowableBox rightChildBox;
        rightChildBox.reset();
        
        for (auto index = endIndex, 
        numLeftChildren = endIndex - startIndex, 
        numRightChildren = 1; 
        
        index > startIndex; 
        
        --index, --numLeftChildren, ++numRightChildren)
        {
            //거꾸로 오면서 오른쪽 상자 면적을 누적 확장
            rightChildBox.growToContain(
            leafNodes[centroidsForAxis[index].leafIndex]);
            
            //미리 기록해둔 왼쪽 면적 (surfaceArea[index -1])과 
            //현재 계산된 오른쪽 면적을 조합해 비용 연산
            auto cost = sahCost(
                surfaceAreas[index - 1], 
                numLeftChildren, 
                rightChildBox.getSurfaceArea(), 
                numRightChildren, parentSurfaceArea);
                
            //최소 비용일 때만 갱신
            if (cost < bestCost)
            {
                bestCost = cost;
                split = Split{numLeftChildren, axis};
            }
            
            /* step 3 -비용이 완전히 같을때 처리
             가끔 3D 공간에서 평평한 평면 위에 물체들이 균일하거나 나열되어
             있으면 어느 칸을 자르든 표면적 비용이 똑같이 나올 수 있다
             이때 트리거가 한쪽으로 길게 늘어지는 기형적인 형태가 되지 않도록
             개수가 좌우 균등하게 분배되는 지점 (balanceCost가 가장 적은곳)
             을 고르도록 예외 처리가 되어 있다
             
            */
            else if (cost == bestCost)
            {
                //비용이 소수점까지 완벽히 똑같다면
                //"개수가 최대한 반반에 가까운 쪽" 을 선택
                auto balanceCost = abs(
                numLeftChildren - ((endIndex - startIndex + 1) / 2)
                );
                
                if (balanceCost < bestBalanceCost)
                {
                    bestBalanceCost = balanceCost;
                    split = Split{numLeftChildren, axis};
                }
            }
        }
    }

	/*
	 step 4 - 최종 결정 및 원본 데이터 순서 동기화
	 
    x,y,z의 수많은 지점 중 승리한 axis,index가 확정되면 이전에 준비했던
    임시 정렬판의 순서를 원본 인덱스 배열(lefatIndices)에 통재로 override
    이제 이 leafIndices는 다음 상자 쪼개기 (build 함수 다음 루프)에서 사용 
	*/
	
	//최종 결정된 승리 축 (split.axis)의 순서대로 원본 leafIndices의
	//순서를 셔플 한다
	
    // Permute the leafIndices of this node's subarray based on the
    // sorted order of leaves along the chosen axis.
    if (split.axis >= 0)
    {
        for (auto i = startIndex; i <= endIndex; ++i)
        {
            leafIndices[i] = centroids[split.axis][i].leafIndex;
        }
    }

    return split;
}

/*
 cost 
 - ray를 쏠때 평균적으로 수행하게 될 trinagle hit 검사 횟수

 [공식]
 상자 A가 부모를 거쳐 광선을 맞을 화률 = 상자A의 표면적 / 부모상자 표면석
 (부모 100, 자식30이면 확률은 30%)
 
 = (왼쪽 상자 맞을 확률 * 왼쪽 삼각형 수 ) + (오른쪽.....)
 = (왼쪽면적/부모면적 * 왼쪽삼각형수) + (오른쪽면적/부모면적 *......)
 = (왼쪽면적 * 왼쪽삼각형수) + (오른쪽면적 * 오른쪽 삼각형수) / 부모면적

*/
float BVH::sahCost(float leftChildSurfaceArea,
                   int32_t numLeftChildren,
                   float rightChildSurfaceArea,
                   int32_t numRightChildren,
                   float parentSurfaceArea) const
{
    return (leftChildSurfaceArea * numLeftChildren 
    + rightChildSurfaceArea * numRightChildren) / parentSurfaceArea;
}

/*
 BVH를 검색하며 ray와 가장 먼저 부딪히는 실제 triangle 찾기
*/
Hit BVH::intersect(const Ray& ray,
                   const Mesh& mesh,
                   float minDistance,
                   float maxDistance) const
{
    Hit hit;
	
	//역수(reciprocal) 미리 계산 (추후 지속적으로 사용)
    Vector3f reciprocalDirection(
        1.0f / ray.direction.x(), 
        1.0f / ray.direction.y(), 
        1.0f / ray.direction.z());
    
    if (ray.direction.x() == -0.0f) 
    {
        reciprocalDirection.x() = std::numeric_limits<float>::infinity();
    }
    
    if (ray.direction.y() == -0.0f)
    {
        reciprocalDirection.y() = std::numeric_limits<float>::infinity();
    } 
    if (ray.direction.z() == -0.0f)
    {
        reciprocalDirection.z() = std::numeric_limits<float>::infinity();
    } 
    
    // ray가 +,-인지 기록 - 양수면 1, 음수면 0
    // 해당 정보는 나중에 '어느쪽 child 상자가 더 가까운가' 를 판단하는데 사용
    int directionSigns[3];
    directionSigns[0] = (ray.direction.x() >= 0) ? 1 : 0;
    directionSigns[1] = (ray.direction.y() >= 0) ? 1 : 0;
    directionSigns[2] = (ray.direction.z() >= 0) ? 1 : 0;

    // We start by checking for intersection with the root node.
    Stack<TraversalTask, kTraversalStackDepth> stack;
    TraversalTask task = { 0, minDistance, maxDistance };

    // In every step of the traversal, we test for intersection against
    // the current node.
    while (true)
    {
        const auto& node = mNodes[task.nodeIndex];
        
        /*
         "bounding box에 ray가 지나가는가?"를 체크
          스치지도 않으면 skip 이후 stack에서 다른상자 꺼냄
        */
        // Check whether the ray passes through the bounding box of the
        // node.
        if (ray.intersect(node.boundingBox(), 
            reciprocalDirection, 
            directionSigns, 
            task.tMin, 
            task.tMax))
        {
            if (node.isLeaf())
            {
                // 실제 삼각형과 광선의 정밀 충돌 거리 계산 (실제 삼각형 검사)
                
                // For leaf nodes, calculate the intersection of the ray
                // and the triangle. If this intersection lies on the ray,
                // and before the current closest hit, make this the
                // current closest hit.
                auto t = ray.intersect(mesh, node.getTriangleIndex());
                if (minDistance <= t && t < hit.distance)
                {
                    hit.distance = t; //더 가까운 충돌 거리로 갱신
                    hit.triangleIndex = node.getTriangleIndex();
                }
            }
            else
            {

                // Based on the ray signs, decide which of the two children
                // is the near child, and which is the far child. Push the
                // far child onto the stack, set the current node to the
                // near child, and continue.
                
                /*
                 가까운 상자부터 검사하고 나중에 먼 상자를 검사
                 - 가까운 상자가 충돌하면 먼 상자는 검사할 필요가 없어서
                   
                 leftChild node idx = parent + offset + 0;
                 rightChild node idx = parent + offset + 1;
                 
                 eg)
                 상자가 x축(0) 기준으로 쪼개져 있고 ray가 
                 오른쪽(x성분이 양수) 를 향해 날아가고 있다고 가정할때
                 - ray가 오른쪽이므로 '왼쪽상자가 가깝고 오른쪽 상자가 멀다'
                 - directSign[splitAixs]값은 = 1
                   
                 [1] 먼 상자 save (stack push)
                 = taskNodeIndex + leftChildOffset + directSigns[splitAxis]
                 = parent index + offset +  1(=오른쪽 자식 상자)
                 = 즉 멀리 있는 오른쪽 상자는 나중에 검사를 위해 stack에 save
                 
                 [2]가까운 상자 (task.nodeIdex 갱신)
                 = taskNodeIndex + lChildOffset + drectSigns[splitAxis] ^ 1
                 = 여기서 1 ^ 1 (XOR) 결과는 0
                 = parent index + offset + 0(=왼쪽 자식 상자)
                 = 루프가 멈추지 않고 곧바로 가장 가까운 외놎ㄱ 상자 내부로
                   파고들게 된다
                   
                 ## if ray 가 left방향으로 날아가면? ##
                 directSigns[spiitAixs] = 0
                 내가 이동할 노드는 0 ^ 1 = 1이 된다
                 따라서 오른쪽상자(가까운쪽)으로 이동 
                */
                
                //주의 - 변수명이 triangle index 이지만 internal node일때는
                // 'chilf node offset'으로 해석
                auto leftChildOffset = node.getTriangleIndex();
                
                // 쪼개는axis 기준 
                auto splitAxis = node.getSplitAxis();
                
                //1. 먼 자식이 상자(far child)를 stack에 save
                stack.push(
                TraversalTask{
                task.nodeIndex + leftChildOffset + 
                directionSigns[splitAxis], 
                task.tMin, 
                task.tMax });
                
                //2. 가까운 자식 상자(near child)로 곧바로 이동
                task.nodeIndex += leftChildOffset +
                 (directionSigns[splitAxis] ^ 1);
                continue;
            }
        }

        // If we've just processed a leaf, pop a new task off the stack.
        // If the stack is empty, stop.
        if (stack.isEmpty())
            break;
            
        /*
         한쪽 줄기 탐색을 마치고 stack에서 task를 꺼낼때
         ray가 도달할수 있는 최대거리를 현재까지 발견한 가장 가까운 충돌거리
         로 강제 제한해 버린다
         이렇게 하면 다음 상자를 검사할때 그 상자가 아무리 깨끗하게
         비어 있어도 "아까 찾은 삼각형보다 뒤에 있네" 하고 ray.intersect 
         조건문에서 차단 된다
        */

        task = stack.pop();
        task.tMax = std::min(task.tMax, hit.distance);
    }

    return hit;
}

/*
 occlusion 상태 체크

 intersect = 가장 가까운점 찾기
 - ray가 box를 뚫고 지나가면서 마주치는 수많은 triangle 중
   "가장 먼저 부딪히는 놈"이 누구진지 정확히 체크
   따라서 loop 전부 돌며 hit.distance 업데이트 필요
   
 isOccluded = 가려졌는지 확인
 - 그림자가 지는지 안지는지 알면 되기 때문에 
   "중간에 한개라도 부딪히는 삼각형이 있는가" 를 체크
   가로 막는 물체 발견시 바로 종료
*/
bool BVH::isOccluded(const Ray& ray,
                     const Mesh& mesh,
                     float minDistance,
                     float maxDistance) const
{

    Vector3f reciprocalDirection(
        1.0f / ray.direction.x(), 
        1.0f / ray.direction.y(), 
        1.0f / ray.direction.z());
        
        
    if (ray.direction.x() == -0.0f)
    {
        reciprocalDirection.x() = std::numeric_limits<float>::infinity();
    } 
    if (ray.direction.y() == -0.0f)
    {
        reciprocalDirection.y() = std::numeric_limits<float>::infinity();
    } 
    if (ray.direction.z() == -0.0f)
    {
        reciprocalDirection.z() = std::numeric_limits<float>::infinity();
    } 

    int directionSigns[3];
    directionSigns[0] = (ray.direction.x() >= 0) ? 1 : 0;
    directionSigns[1] = (ray.direction.y() >= 0) ? 1 : 0;
    directionSigns[2] = (ray.direction.z() >= 0) ? 1 : 0;

    // We start by checking for intersection with the root node.
    BVHNode* stack[kTraversalStackDepth];
    auto top = 0;
    auto node = const_cast<BVHNode*>(&mNodes[0]);

    // In every step of the traversal, we test for intersection against
    // the current node.
    while (true)
    {
        float tMin = minDistance;
        float tMax = maxDistance;
        
        // Check whether the ray passes through the bounding box of 
        //the node
        if (ray.intersect(node->boundingBox(), 
            reciprocalDirection, directionSigns, tMin, tMax))
        {
            if (node->isLeaf())
            {
                // For leaf nodes, calculate the intersection of the ray
                // and the triangle. If this intersection lies on the ray,
                // the ray is occluded.
                auto t = ray.intersect(mesh, node->getTriangleIndex());
                if (minDistance <= t && t < maxDistance)
                    return true;
                    //무엇인가 부딪히게 확인되면 바로 종료
            }
            else
            {
                //sahCost의 로직과 동일 가까운거 상자 먼저 체크
                
                // Based on the ray signs, decide which of the two children
                // is the near child, and which is the far child. Push the
                // far child onto the stack, set the current node to the
                // near child, and continue.
                auto leftChildOffset = node->getTriangleIndex();
                auto splitAxis = node->getSplitAxis();
                stack[top++] = node + leftChildOffset + 
                directionSigns[splitAxis];
                
                node += leftChildOffset + (directionSigns[splitAxis] ^ 1);
                continue;
            }
        }

        // If we've just processed a leaf, pop a new task off the stack.
        // If the stack is empty, stop.
        if (top <= 0)
            break;

        node = stack[--top];
    }

    return false;
}

bool BVH::isOccluded(const Vector3f& start,
                     const Vector3f& end,
                     const Mesh& mesh) const
{
    auto ray = Ray{ start, Vector3f::unitVector(end - start) };
    auto distance = (end - start).length();
    return isOccluded(ray, mesh, 0.0f, distance);
}

/*
 BVH를 검색하며 collison overlap 되는 triangle 찾기
*/
bool BVH::intersect(const Box& box,
                    const Mesh& mesh) const
{
    Stack<int32_t, kTraversalStackDepth> stack;

    auto nodeIndex = 0;

    while (true)
    {
        const auto& node = mNodes[nodeIndex];
        
        //AABB 충돌검사 (box, box)
        //box와 node.boundingBox()가 겹치는지 확인
        //겹치지 않는다면 수많은 하위 노드 skip
        if (boxIntersectsBox(box, node.boundingBox()))
        {
            if (node.isLeaf())
            {
                /*정밀검사 (box , leaf)
                 leaf node에 도달하면 node의 triangle과 실제 겹치는지
                 검사를 수행
                 isOccluded처럼 하나라도 겹치면 true
                */
                if (boxIntersectsTriangle(box, 
                       mesh, 
                        node.getTriangleIndex()))
                   {
                       return true;
                   }
                    
            }
            else
            {
                auto splitAxis = node.getSplitAxis();
                
                /*
                 이전 코드처럼 ^1 대신 std::swap을 쓰는 이유?
                 
                 ray는 한방향으로 뻗어나가는 성질을 가졌기 때문에
                 direction에 +.-가 있어서 가깝고 멀고를 정할수 있다
                 반면 상자는 부피자체. "어느 자식이 가까운가?"를 알기 위해서는
                 "내가 던진 상자의 중심이 부모상자 분할 경계선보다 어느쪽에
                 치우쳐 있는가"라는 ##좌표 크기 비교##가 필요
                */

                auto nearChildOffset = node.getTriangleIndex();
                auto farChildOffset = nearChildOffset + 1;
                if (box.minCoordinates[splitAxis] >
                    node.boundingBox().minCoordinates[splitAxis])
                {
                    std::swap(nearChildOffset, farChildOffset);
                }

                stack.push(nodeIndex + farChildOffset);
                nodeIndex += nearChildOffset;
                continue;
            }
        }

        if (stack.isEmpty())
            break;

        nodeIndex = stack.pop();
    }

    return false;
}

bool BVH::boxIntersectsBox(const Box& box1,
                           const Box& box2)
{
    auto dx = std::max(0.0f, 
    box2.minCoordinates.x() - box1.maxCoordinates.x()) + 
    std::max(0.0f, box1.minCoordinates.x() - box2.maxCoordinates.x());
    
    auto dy = std::max(0.0f, 
    box2.minCoordinates.y() - box1.maxCoordinates.y()) + 
    std::max(0.0f, box1.minCoordinates.y() - box2.maxCoordinates.y());
    
    auto dz = std::max(0.0f, 
    box2.minCoordinates.z() - box1.maxCoordinates.z()) + 
    std::max(0.0f, box1.minCoordinates.z() - box2.maxCoordinates.z());

    return (dx == 0.0f && dy == 0.0f && dz == 0.0f);
}

/*AaBB 와 triangle 실제 겹치는가 체크 (복잡한 연산) */
bool BVH::boxIntersectsTriangle(const Box& box,
                                const Mesh& mesh,
                                int32_t triangleIndex)
{
    // if the bounding box of the triangle doesn't intersect the box, 
    // we shouldn't have reached this function

    // if the plane of the triangle doesn't intersect the box, stop

    auto v0 = mesh.triangleVertex(triangleIndex, 0);
    auto v1 = mesh.triangleVertex(triangleIndex, 1);
    auto v2 = mesh.triangleVertex(triangleIndex, 2);
    auto normal = mesh.normal(triangleIndex);
    auto extents = box.extents();

    auto criticalPointOffset = Vector3f(0.0f, 0.0f, 0.0f);
    if (normal.x() > 0.0f)
    {
        criticalPointOffset.x() = extents.x();
    }
    if (normal.y() > 0.0f)
    {
        criticalPointOffset.y() = extents.y();
    }
    if (normal.z() > 0.0f)
    {
        criticalPointOffset.z() = extents.z();
    }

    auto np = Vector3f::dot(normal, box.minCoordinates);
    auto d1 = Vector3f::dot(normal, criticalPointOffset - v0);
    auto d2 = Vector3f::dot(normal, (extents - criticalPointOffset) - v0);

    if ((np + d1) * (np + d2) > 0.0f)
        return false;

    // actual intersection tests

    // xy plane

    Vector3f e0 = v1 - v0;
    Vector3f e1 = v2 - v1;
    Vector3f e2 = v0 - v2;

    auto nxy0 = Vector2f(-e0.y(), e0.x());
    auto nxy1 = Vector2f(-e1.y(), e1.x());
    auto nxy2 = Vector2f(-e2.y(), e2.x());
    if (normal.z() < 0.0f)
    {
        nxy0 *= -1.0f;
        nxy1 *= -1.0f;
        nxy2 *= -1.0f;
    }

    auto dxy0 = -Vector2f::dot(nxy0, 
    Vector2f(v0.x(), 
    v0.y())) + std::max(0.0f, 
    extents.x() * nxy0.x()) + std::max(0.0f, extents.y() * nxy0.y());
    
    auto dxy1 = -Vector2f::dot(nxy1, 
    Vector2f(v1.x(), 
    v1.y())) + std::max(0.0f, extents.x() * nxy1.x()) + 
    std::max(0.0f, extents.y() * nxy1.y());
    
    auto dxy2 = -Vector2f::dot(nxy2, 
    Vector2f(v2.x(), v2.y())) + std::max(0.0f, extents.x() * 
    nxy2.x()) + std::max(0.0f, extents.y() * nxy2.y());

    if (Vector2f::dot(nxy0, Vector2f(box.minCoordinates.x(),
        box.minCoordinates.y())) + dxy0 < 0.0f ||
        Vector2f::dot(nxy1, Vector2f(box.minCoordinates.x(), 
        box.minCoordinates.y())) + dxy1 < 0.0f ||
        Vector2f::dot(nxy2, Vector2f(box.minCoordinates.x(), 
        box.minCoordinates.y())) + dxy2 < 0.0f)
    {
        return false;
    }

    // yz plane

    auto nyz0 = Vector2f(-e0.z(), e0.y());
    auto nyz1 = Vector2f(-e1.z(), e1.y());
    auto nyz2 = Vector2f(-e2.z(), e2.y());
    if (normal.x() < 0.0f)
    {
        nyz0 *= -1.0f;
        nyz1 *= -1.0f;
        nyz2 *= -1.0f;
    }

    auto dyz0 = -Vector2f::dot(nyz0, 
    Vector2f(v0.y(), v0.z())) + std::max(0.0f, extents.y() * 
    nyz0.x()) + std::max(0.0f, extents.z() * nyz0.y());
    
    auto dyz1 = -Vector2f::dot(nyz1, 
    Vector2f(v1.y(), v1.z())) + std::max(0.0f, extents.y() * 
    nyz1.x()) + std::max(0.0f, extents.z() * nyz1.y());
    
    auto dyz2 = -Vector2f::dot(nyz2, 
    Vector2f(v2.y(), v2.z())) + std::max(0.0f, extents.y() * 
    nyz2.x()) + std::max(0.0f, extents.z() * nyz2.y());

    if (Vector2f::dot(nyz0, 
        Vector2f(box.minCoordinates.y(), 
                 box.minCoordinates.z())) + dyz0 < 0.0f ||
             
        Vector2f::dot(nyz1, 
        Vector2f(box.minCoordinates.y(),
                 box.minCoordinates.z())) + dyz1 < 0.0f ||
        
        Vector2f::dot(nyz2, 
        Vector2f(box.minCoordinates.y(), 
                 box.minCoordinates.z())) + dyz2 < 0.0f)
    {
        return false;
    }

    // zx plane

    auto nzx0 = Vector2f(-e0.x(), e0.z());
    auto nzx1 = Vector2f(-e1.x(), e1.z());
    auto nzx2 = Vector2f(-e2.x(), e2.z());
    if (normal.y() < 0.0f)
    {
        nzx0 *= -1.0f;
        nzx1 *= -1.0f;
        nzx2 *= -1.0f;
    }

    auto dzx0 = -Vector2f::dot(nzx0, 
    Vector2f(v0.z(), 
    v0.x())) + std::max(0.0f, extents.z() * 
    nzx0.x()) + std::max(0.0f, extents.x() * nzx0.y());
    
    auto dzx1 = -Vector2f::dot(nzx1, 
    Vector2f(v1.z(), v1.x())) + std::max(0.0f, extents.z() * 
    nzx1.x()) + std::max(0.0f, extents.x() * nzx1.y());
    
    auto dzx2 = -Vector2f::dot(nzx2, 
    Vector2f(v2.z(), v2.x())) + std::max(0.0f, extents.z() * 
    nzx2.x()) + std::max(0.0f, extents.x() * nzx2.y());

    if (Vector2f::dot(nzx0, 
        Vector2f(box.minCoordinates.z(), 
                 box.minCoordinates.x())) + dzx0 < 0.0f ||
             
        Vector2f::dot(nzx1, 
        Vector2f(box.minCoordinates.z(), 
                 box.minCoordinates.x())) + dzx1 < 0.0f ||
                 
        Vector2f::dot(nzx2, 
        Vector2f(box.minCoordinates.z(), 
                 box.minCoordinates.x())) + dzx2 < 0.0f)
    {
        return false;
    }

    return true;
}

}// namespace

```

---




