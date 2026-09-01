#include <metal_stdlib>
using namespace metal;

// SIMD-tiled Dot Product & Cosine Similarity Compute Kernel
kernel void cosine_similarity_kernel(
    device const float* query_vector      [[buffer(0)]],
    device const float* matrix_vectors    [[buffer(1)]],
    device float*       similarity_scores [[buffer(2)]],
    constant uint&      vector_dim        [[buffer(3)]],
    constant uint&      num_entities      [[buffer(4)]],
    uint                gid               [[thread_position_in_grid]])
{
    if (gid >= num_entities) return;

    uint offset = gid * vector_dim;
    float dot_product = 0.0f;
    float query_norm_sq = 0.0f;
    float target_norm_sq = 0.0f;

    // SIMD 4-wide vector loop
    uint i = 0;
    for (; i + 4 <= vector_dim; i += 4) {
        float4 q = float4(query_vector[i], query_vector[i+1], query_vector[i+2], query_vector[i+3]);
        float4 t = float4(matrix_vectors[offset + i], matrix_vectors[offset + i+1], matrix_vectors[offset + i+2], matrix_vectors[offset + i+3]);
        
        dot_product += dot(q, t);
        query_norm_sq += dot(q, q);
        target_norm_sq += dot(t, t);
    }

    // Scalar remainder
    for (; i < vector_dim; i++) {
        float q = query_vector[i];
        float t = matrix_vectors[offset + i];
        dot_product += q * t;
        query_norm_sq += q * q;
        target_norm_sq += t * t;
    }

    float norm_prod = sqrt(query_norm_sq) * sqrt(target_norm_sq);
    similarity_scores[gid] = (norm_prod > 1e-7f) ? (dot_product / norm_prod) : 0.0f;
}
