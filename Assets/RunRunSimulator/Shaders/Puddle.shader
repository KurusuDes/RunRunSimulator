Shader "MoriMonchi/Puddle"
{
    Properties
    {
        _WaterColor ("Water Color", Color) = (0.10, 0.16, 0.20, 1)
        _WetColor ("Wet Ground Color", Color) = (0.05, 0.05, 0.04, 1)
        _CenterAlpha ("Center Alpha", Range(0,1)) = 0.18
        _WetAlpha ("Wet Ring Alpha", Range(0,1)) = 0.28
        _Radius ("Radius", Range(0.2,1)) = 0.78
        _Softness ("Edge Softness", Range(0.01,0.5)) = 0.07
        _WetWidth ("Wet Ring Width", Range(0,0.5)) = 0.07
        _EdgeNoise ("Edge Noise", Range(0,1)) = 0.42
        _EdgeNoiseScale ("Edge Noise Scale", Float) = 1.7
        _Roughness ("Roughness", Range(0,1)) = 0.04
        _ReflectionStrength ("Reflection Strength", Range(0,2)) = 1.1
        _SpecPower ("Specular Power", Float) = 220
        _SpecStrength ("Specular Strength", Range(0,4)) = 1.6
        _RippleStrength ("Ripple Strength", Range(0,1)) = 0.35
        _RippleFrequency ("Ripple Frequency", Float) = 38
        _RippleSpeed ("Ripple Speed", Float) = 0.55
        _RippleRate ("Drops Per Second", Float) = 0.6
        _WobbleStrength ("Surface Wobble", Range(0,1)) = 0.08
        _SkyHorizon ("Sky Horizon", Color) = (0.78, 0.86, 0.95, 1)
        _SkyZenith ("Sky Zenith", Color) = (0.36, 0.55, 0.86, 1)
        _FresnelPower ("Fresnel Power", Range(1,8)) = 3
        _RimColor ("Edge Highlight", Color) = (0.9, 0.95, 1, 1)
        _RimStrength ("Edge Highlight Strength", Range(0,2)) = 0.6
        _ReflectionTint ("Reflection Tint", Color) = (0.82, 0.9, 1, 1)
        _Fade ("Fade", Range(0,1)) = 1
    }
    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent+50" "RenderPipeline"="UniversalPipeline" "IgnoreProjector"="True" }
        Blend One OneMinusSrcAlpha
        ZWrite Off
        Cull Off
        Offset -1, -1

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_fog
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BLENDING
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BOX_PROJECTION

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _WaterColor;
                half4 _WetColor;
                half _CenterAlpha;
                half _WetAlpha;
                half _Radius;
                half _Softness;
                half _WetWidth;
                half _EdgeNoise;
                float _EdgeNoiseScale;
                half _Roughness;
                half _ReflectionStrength;
                float _SpecPower;
                half _SpecStrength;
                half _RippleStrength;
                float _RippleFrequency;
                float _RippleSpeed;
                float _RippleRate;
                half _WobbleStrength;
                half4 _SkyHorizon;
                half4 _SkyZenith;
                half _FresnelPower;
                half4 _RimColor;
                half _RimStrength;
                half4 _ReflectionTint;
                half _Fade;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                float seed : TEXCOORD2;
                half fogFactor : TEXCOORD3;
            };

            float Hash21(float2 p)
            {
                p = frac(p * float2(123.34, 456.21));
                p += dot(p, p + 45.32);
                return frac(p.x * p.y);
            }

            float2 Hash22(float2 p)
            {
                float n = Hash21(p);
                return float2(n, Hash21(p + n + 17.1));
            }

            float ValueNoise(float2 p)
            {
                float2 i = floor(p);
                float2 f = frac(p);
                float2 u = f * f * (3.0 - 2.0 * f);
                float a = Hash21(i);
                float b = Hash21(i + float2(1, 0));
                float c = Hash21(i + float2(0, 1));
                float d = Hash21(i + float2(1, 1));
                return lerp(lerp(a, b, u.x), lerp(c, d, u.x), u.y);
            }

            float Fbm(float2 p)
            {
                float v = 0.0;
                float a = 0.55;
                for (int k = 0; k < 4; k++)
                {
                    v += a * ValueNoise(p);
                    p = p * 2.03 + 11.7;
                    a *= 0.5;
                }
                return v;
            }

            float Shape(float2 p, float seed)
            {
                float n = Fbm(p * _EdgeNoiseScale + seed * 31.7);
                return length(p) + (n - 0.5) * _EdgeNoise;
            }

            Varyings Vert(Attributes input)
            {
                Varyings o;
                VertexPositionInputs v = GetVertexPositionInputs(input.positionOS.xyz);
                o.positionCS = v.positionCS;
                o.positionWS = v.positionWS;
                o.uv = input.uv;
                float3 origin = float3(UNITY_MATRIX_M._m03, UNITY_MATRIX_M._m13, UNITY_MATRIX_M._m23);
                o.seed = Hash21(origin.xz * 0.731 + 3.17);
                o.fogFactor = ComputeFogFactor(v.positionCS.z);
                return o;
            }

            float2 RippleGradient(float2 p, float seed)
            {
                float2 grad = 0;
                float t = _Time.y * _RippleRate;
                [unroll]
                for (int i = 0; i < 3; i++)
                {
                    float slot = floor(t + i * 0.333);
                    float age = frac(t + i * 0.333) / max(_RippleRate, 0.001);
                    float2 center = (Hash22(float2(slot, seed * 97.0 + i)) - 0.5) * 0.9;
                    float2 d = p - center;
                    float dist = length(d) + 1e-4;
                    float front = age * _RippleSpeed;
                    float band = exp(-abs(dist - front) * 18.0);
                    float decay = saturate(1.0 - age * _RippleRate * 1.2);
                    float wave = cos((dist - front) * _RippleFrequency);
                    grad += (d / dist) * wave * band * decay;
                }
                return grad;
            }

            half4 Frag(Varyings i, bool frontFace : SV_IsFrontFace) : SV_Target
            {
                float2 p = i.uv * 2.0 - 1.0;
                float edge = Shape(p, i.seed);

                float inner = _Radius - _Softness;
                half mask = 1.0 - smoothstep(inner, _Radius, edge);
                half water = 1.0 - smoothstep(inner - _WetWidth - _Softness, inner - _WetWidth, edge);
                if (mask <= 0.001) discard;

                float2 grad = RippleGradient(p, i.seed) * _RippleStrength;
                float2 wob = float2(ValueNoise(p * 4.0 + _Time.y * 0.35 + i.seed * 9.0), ValueNoise(p * 4.0 - _Time.y * 0.31 + 5.3)) - 0.5;
                grad += wob * _WobbleStrength;
                grad *= water;

                float3 n = normalize(float3(-grad.x, 1.0, -grad.y));
                float3 v = normalize(GetWorldSpaceViewDir(i.positionWS));
                float ndv = saturate(dot(n, v));
                half fresnel = saturate(0.08 + 0.92 * pow(1.0 - ndv, _FresnelPower));

                float3 r = reflect(-v, n);
                half3 sky = lerp(_SkyHorizon.rgb, _SkyZenith.rgb, saturate(r.y * 1.4));
                half3 probe = GlossyEnvironmentReflection(r, i.positionWS, _Roughness, 1.0, GetNormalizedScreenSpaceUV(i.positionCS));
                half3 refl = lerp(sky, probe, saturate(r.y < 0.15 ? 1.0 : 0.85)) * _ReflectionTint.rgb * _ReflectionStrength;

                Light light = GetMainLight(TransformWorldToShadowCoord(i.positionWS));
                float3 h = normalize(light.direction + v);
                half spec = pow(saturate(dot(n, h)), _SpecPower) * _SpecStrength * light.shadowAttenuation;
                half3 specCol = spec * light.color;

                float inside = (inner - _WetWidth) - edge;
                half rim = exp(-max(inside, 0.0) * 55.0) * water * _RimStrength * (0.35 + fresnel);
                half3 sheen = (refl * fresnel + specCol + rim * _RimColor.rgb) * water;
                half absorb = lerp(_WetAlpha, _CenterAlpha, water);
                half3 tint = lerp(_WetColor.rgb, _WaterColor.rgb, water);
                half k = mask * _Fade;
                half alpha = saturate(absorb + fresnel * 0.35 * water) * k;
                half3 col = tint * alpha + sheen * k;
                col = MixFogColor(col, half3(0,0,0), i.fogFactor);
                return half4(col, alpha);
            }
            ENDHLSL
        }
    }
}
