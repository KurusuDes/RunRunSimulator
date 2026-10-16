Shader "MoriMonchi/CartoonGlass"
{
    Properties
    {
        _Color ("Color", Color) = (0.62, 0.82, 0.95, 0.38)
        _TopColor ("Top Color", Color) = (0.85, 0.95, 1, 0.5)
        _StreakColor ("Streak Color", Color) = (1, 1, 1, 0.75)
        _StreakScale ("Streak Scale", Float) = 1.4
        _StreakWidth ("Streak Width", Range(0, 0.5)) = 0.16
        _StreakThin ("Streak Thin", Range(0, 0.2)) = 0.05
        _StreakGap ("Streak Gap", Range(0, 1)) = 0.28
        _Slant ("Slant", Float) = 1.0
        _FresnelColor ("Fresnel Color", Color) = (1, 1, 1, 0.35)
        _FresnelPower ("Fresnel Power", Float) = 3
        _GradientHeight ("Gradient Height", Float) = 1.2
    }
    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent" "RenderPipeline"="UniversalPipeline" "IgnoreProjector"="True" }
        Blend SrcAlpha OneMinusSrcAlpha
        ZWrite Off
        Cull Back

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_fog

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _Color;
                half4 _TopColor;
                half4 _StreakColor;
                float _StreakScale;
                float _StreakWidth;
                float _StreakThin;
                float _StreakGap;
                float _Slant;
                half4 _FresnelColor;
                float _FresnelPower;
                float _GradientHeight;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionOS : TEXCOORD0;
                float3 normalOS : TEXCOORD1;
                float3 normalWS : TEXCOORD2;
                float3 positionWS : TEXCOORD3;
                half fogFactor : TEXCOORD4;
            };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                VertexPositionInputs v = GetVertexPositionInputs(input.positionOS.xyz);
                o.positionCS = v.positionCS;
                o.positionWS = v.positionWS;
                o.positionOS = input.positionOS.xyz;
                o.normalOS = input.normalOS;
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                o.fogFactor = ComputeFogFactor(v.positionCS.z);
                return o;
            }

            float Band(float f, float width, float aa)
            {
                return 1.0 - smoothstep(width * 0.5 - aa, width * 0.5 + aa, abs(f - 0.5));
            }

            half4 Frag(Varyings i) : SV_Target
            {
                float3 n = normalize(i.normalOS);
                float3 t = cross(n, float3(0, 1, 0));
                t = dot(t, t) < 0.0001 ? float3(1, 0, 0) : normalize(t);
                float u = dot(i.positionOS, t);
                float v = i.positionOS.y;
                float d = (u + v * _Slant) * _StreakScale;
                float f = frac(d);
                float aa = max(fwidth(d), 0.0001);

                float wide = Band(f, _StreakWidth * 2.0, aa);
                float thin = Band(frac(f + _StreakGap + 0.5), _StreakThin * 2.0, aa);
                half mask = saturate(wide + thin);

                half grad = saturate(frac(v / max(_GradientHeight, 0.0001)));
                half4 baseCol = lerp(_Color, _TopColor, grad);

                float3 nWS = normalize(i.normalWS);
                float3 viewWS = normalize(GetWorldSpaceViewDir(i.positionWS));
                half fres = pow(saturate(1.0 - saturate(dot(nWS, viewWS))), _FresnelPower);

                Light light = GetMainLight();
                half ndl = saturate(dot(nWS, light.direction));
                half3 rgb = baseCol.rgb * lerp(0.85, 1.0, ndl);

                half streakA = mask * _StreakColor.a;
                rgb = lerp(rgb, _StreakColor.rgb, streakA);
                half fresA = fres * _FresnelColor.a;
                rgb = lerp(rgb, _FresnelColor.rgb, fresA);

                half alpha = max(baseCol.a, max(streakA, fresA));
                rgb = MixFog(rgb, i.fogFactor);
                return half4(rgb, alpha);
            }
            ENDHLSL
        }
    }
}
