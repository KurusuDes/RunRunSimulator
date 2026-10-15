Shader "MoriMonchi/ArenaGrass"
{
    Properties
    {
        _Ramp ("Palette Ramp", 2D) = "white" {}
        _RampInfluence ("Ramp Influence", Range(0,1)) = 1
        _BaseColor ("Base Color", Color) = (0.32,0.55,0.24,1)
        _Tint ("Tint", Color) = (1,1,1,1)
        _RootShade ("Root Shade", Range(0,1)) = 0.45
        _TipLift ("Tip Lift", Range(0,1)) = 0.95
        _WindStrength ("Wind Strength", Float) = 0.12
        _WindSpeed ("Wind Speed", Float) = 1.2
        _WindScale ("Wind Scale", Float) = 0.35
        _TrampleBend ("Trample Bend", Float) = 0.9
        _TrampleFlatten ("Trample Flatten", Range(0,1)) = 0.75
        _TrampleShade ("Trample Shade", Range(0,1)) = 0.25
        _ShadowStrength ("Shadow Strength", Range(0,1)) = 0.75
        _ToonStep ("Toon Step", Range(0,1)) = 0.45
        _ToonFeather ("Toon Feather", Range(0.001,0.5)) = 0.2
        _ShadeTint ("Shade Tint", Color) = (0.58,0.56,0.68,1)
        _ShadeLight ("Shade Light", Range(0,1)) = 0.45
        _LitLight ("Lit Light", Range(0,2)) = 0.72
        _GustDir ("Gust Direction", Vector) = (1,0,0.35,0)
        _GustScale ("Gust Scale", Float) = 0.07
        _GustSpeed ("Gust Speed", Float) = 2.2
        _GustStrength ("Gust Strength", Float) = 0.32
        _GustSheen ("Gust Sheen", Range(0,1)) = 0.28
        _PatchScale ("Patch Scale", Float) = 0.045
        _PatchTint ("Patch Tint", Color) = (1.12,1.06,0.78,1)
        _PatchAmount ("Patch Amount", Range(0,1)) = 0.35
        _TipGlow ("Tip Glow", Range(0,1)) = 0.3
        _TipGlowColor ("Tip Glow Color", Color) = (1,0.95,0.6,1)
        _NormalBlend ("Terrain Normal Blend", Range(0,1)) = 0.85
        _RootColor ("Root Color (ground)", Color) = (0.43,0.56,0.35,1)
        _RootShadeColor ("Root Shade Color (ground shade)", Color) = (0.345,0.437,0.289,1)
        _RootBlend ("Root Blend", Range(0,1)) = 0
        _RootHeight ("Root Height", Range(0.01,1)) = 0.35
        _Saturation ("Saturation", Range(0,2)) = 1
        _TipColor ("Tip Color", Color) = (1,1,1,1)
        _TipColorBlend ("Tip Color Blend", Range(0,1)) = 0
        _HueScale ("Hue Noise Scale", Float) = 0.12
        _HueColor ("Hue Patch Color", Color) = (0.85,1.0,0.8,1)
        _HueAmount ("Hue Amount", Range(0,1)) = 0
        _BladeVariation ("Blade Variation", Range(0,0.3)) = 0.05
        _FlowerTint ("Flower Tint", Color) = (1,1,1,1)
        _FlowerLift ("Flower Lift", Range(0,1)) = 0.15
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" "Queue"="Geometry" "RenderPipeline"="UniversalPipeline" }
        Cull Off

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fog

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                half4 _Tint;
                half _RampInfluence;
                half _RootShade;
                half _TipLift;
                half _WindStrength;
                half _WindSpeed;
                half _WindScale;
                half _TrampleBend;
                half _TrampleFlatten;
                half _TrampleShade;
                half _ShadowStrength;
                half _ToonStep;
                half _ToonFeather;
                half4 _ShadeTint;
                half _ShadeLight;
                half _LitLight;
                float4 _GustDir;
                float _GustScale;
                float _GustSpeed;
                float _GustStrength;
                half _GustSheen;
                float _PatchScale;
                half4 _PatchTint;
                half _PatchAmount;
                half _TipGlow;
                half4 _TipGlowColor;
                half _NormalBlend;
                half4 _RootColor;
                half4 _RootShadeColor;
                half _RootBlend;
                half _RootHeight;
                half _Saturation;
                half4 _TipColor;
                half _TipColorBlend;
                float _HueScale;
                half4 _HueColor;
                half _HueAmount;
                half _BladeVariation;
                half4 _FlowerTint;
                half _FlowerLift;
            CBUFFER_END

            float4 _ArenaFogCenter;
            float4 _ArenaFogColor;
            float _ArenaFogInner;
            float _ArenaFogOuter;
            float _ArenaFogStrength;
            float _ArenaFogDim;

            float4 _ArenaTrampleArea;

            TEXTURE2D(_Ramp);
            SAMPLER(sampler_Ramp);
            TEXTURE2D(_ArenaTrampleTex);
            SAMPLER(sampler_ArenaTrampleTex);

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
                half4 color : COLOR;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                float3 normalWS : TEXCOORD2;
                float fogFactor : TEXCOORD3;
                half2 blade : TEXCOORD4;
                half gust : TEXCOORD5;
                half4 vcolor : TEXCOORD6;
            };

            float Hash21(float2 p)
            {
                return frac(sin(dot(p, float2(127.1, 311.7))) * 43758.5453);
            }

            float ValueNoise(float2 p)
            {
                float2 i = floor(p);
                float2 f = frac(p);
                float2 u = f * f * (3.0 - 2.0 * f);
                float a = Hash21(i);
                float b = Hash21(i + float2(1.0, 0.0));
                float c = Hash21(i + float2(0.0, 1.0));
                float d = Hash21(i + float2(1.0, 1.0));
                return lerp(lerp(a, b, u.x), lerp(c, d, u.x), u.y);
            }

            float4 SampleTrample(float3 positionWS)
            {
                if (_ArenaTrampleArea.z <= 0.0) return 0.0;
                float2 uv = (positionWS.xz - _ArenaTrampleArea.xy) * _ArenaTrampleArea.zw;
                if (any(uv < 0.0) || any(uv > 1.0)) return 0.0;
                return SAMPLE_TEXTURE2D_LOD(_ArenaTrampleTex, sampler_ArenaTrampleTex, uv, 0);
            }

            Varyings Vert(Attributes input)
            {
                Varyings output;

                float3 positionWS = TransformObjectToWorld(input.positionOS.xyz);
                float height = max(input.positionOS.y, 0.0);
                float along = saturate(input.uv.y);
                float curve = along * along;

                float4 trample = SampleTrample(positionWS);
                float flatten = saturate(trample.b);

                float phase = _Time.y * _WindSpeed + positionWS.x * _WindScale + positionWS.z * _WindScale * 0.7 + input.color.r * 6.2831;
                float sway = sin(phase) * 0.6 + sin(phase * 2.3 + 1.3) * 0.4;
                float breeze = 1.0 - flatten * 0.8;

                positionWS.x += sway * _WindStrength * curve * breeze;
                positionWS.z += cos(phase * 0.8) * _WindStrength * 0.5 * curve * breeze;

                float2 gustDir = _GustDir.xz / max(length(_GustDir.xz), 0.0001);
                float2 gustPerp = float2(-gustDir.y, gustDir.x);
                float2 gustCoord = float2(dot(positionWS.xz, gustDir) - _Time.y * _GustSpeed, dot(positionWS.xz, gustPerp) * 0.45) * _GustScale;
                float gust = smoothstep(0.4, 0.8, ValueNoise(gustCoord));
                positionWS.xz += gustDir * curve * gust * _GustStrength * breeze;

                positionWS.xz += clamp(trample.rg, -1.0, 1.0) * _TrampleBend * curve;
                positionWS.y -= flatten * _TrampleFlatten * height;

                output.positionWS = positionWS;
                output.positionCS = TransformWorldToHClip(positionWS);
                output.normalWS = normalize(lerp(TransformObjectToWorldNormal(input.normalOS), float3(0.0, 1.0, 0.0), _NormalBlend));
                output.uv = input.uv;
                output.fogFactor = ComputeFogFactor(output.positionCS.z);
                output.blade = half2(input.color.r, flatten);
                output.gust = gust;
                output.vcolor = input.color;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half along = saturate(input.uv.y);
                half isFlower = input.vcolor.a < 0.5 ? 1.0 : 0.0;
                half variation = lerp(1.0 - _BladeVariation, 1.0 + _BladeVariation, input.blade.x);
                half key = saturate(lerp(_RootShade, _TipLift, along) * variation);

                half3 albedo;
                if (isFlower > 0.5)
                {
                    albedo = input.vcolor.rgb * _FlowerTint.rgb;
                }
                else
                {
                    half3 ramp = SAMPLE_TEXTURE2D(_Ramp, sampler_Ramp, float2(key, 0.5)).rgb;
                    albedo = lerp(_BaseColor.rgb * key, ramp, _RampInfluence) * _Tint.rgb;
                    half luma = dot(albedo, half3(0.2126, 0.7152, 0.0722));
                    albedo = lerp(luma.xxx, albedo, _Saturation);
                    albedo = lerp(albedo, albedo * _TipColor.rgb, smoothstep(0.4, 1.0, along) * _TipColorBlend);
                    half patch = smoothstep(0.3, 0.7, ValueNoise(input.positionWS.xz * _PatchScale));
                    albedo = lerp(albedo, albedo * _PatchTint.rgb, patch * _PatchAmount);
                    half hn = ValueNoise(input.positionWS.xz * _HueScale + 17.3);
                    albedo = lerp(albedo, albedo * _HueColor.rgb, smoothstep(0.35, 0.75, hn) * _HueAmount);
                }
                albedo *= lerp(1.0, 1.0 - _TrampleShade, input.blade.y);

                float4 shadowCoord = TransformWorldToShadowCoord(input.positionWS);
                Light mainLight = GetMainLight(shadowCoord);
                half3 normalWS = normalize(input.normalWS);
                half attenuation = lerp(1.0, mainLight.shadowAttenuation * mainLight.distanceAttenuation, _ShadowStrength);
                half wrapped = dot(normalWS, mainLight.direction) * 0.5 + 0.5;
                half lit = smoothstep(_ToonStep - _ToonFeather, _ToonStep + _ToonFeather, wrapped * attenuation);
                half3 ambient = SampleSH(normalWS);

                half3 litColor = albedo * (mainLight.color * _LitLight + ambient);
                half3 shadeColor = albedo * _ShadeTint.rgb * (mainLight.color * _ShadeLight + ambient);
                shadeColor = lerp(shadeColor, litColor, _FlowerLift * isFlower);
                half3 color = lerp(shadeColor, litColor, lit);

                color *= 1.0 + _GustSheen * input.gust * along;

                half rootT = (1.0 - smoothstep(0.0, _RootHeight, along)) * _RootBlend * (1.0 - isFlower);
                half3 groundLit = lerp(_RootShadeColor.rgb, _RootColor.rgb, lit) * (mainLight.color * 0.5 + 0.5);
                color = lerp(color, groundLit, rootT);

                half3 viewDirWS = normalize(_WorldSpaceCameraPos - input.positionWS);
                half backlight = saturate(dot(-viewDirWS, mainLight.direction) * 0.5 + 0.5);
                color += _TipGlowColor.rgb * mainLight.color * _TipGlow * lerp(1.0, 0.5, isFlower) * along * along * backlight * backlight;

                float dFog = distance(input.positionWS.xz, _ArenaFogCenter.xz);
                float tFog = 0.0;
                if (_ArenaFogOuter > _ArenaFogInner)
                {
                    tFog = saturate((dFog - _ArenaFogInner) / (_ArenaFogOuter - _ArenaFogInner));
                    tFog = smoothstep(0.0, 1.0, tFog);
                }
                color *= lerp(1.0, 1.0 - _ArenaFogDim, tFog);
                color = lerp(color, _ArenaFogColor.rgb, tFog * _ArenaFogStrength);

                color = MixFog(color, input.fogFactor);
                return half4(color, 1.0);
            }
            ENDHLSL
        }
    }

    FallBack Off
}
