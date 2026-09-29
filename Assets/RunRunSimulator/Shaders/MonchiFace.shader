Shader "MoriMonchi/MonchiFace"
{
    Properties
    {
        _MainTex ("Current Texture", 2D) = "white" {}
        _PrevTex ("Previous Texture", 2D) = "white" {}
        _FaceT ("Face T", Range(0,1)) = 1
        _FaceMode ("Face Mode (0 blink, 1 pop)", Float) = 0
        _Overshoot ("Overshoot", Float) = 0.25
        _EyeY ("Eye Y", Float) = 0.5
        _EyeLX ("Eye Left X", Float) = 0.236
        _EyeRX ("Eye Right X", Float) = 0.764
        _BandMin ("Band Min", Float) = 0.43
        _BandMax ("Band Max", Float) = 0.707
    }
    SubShader
    {
        Tags { "Queue"="Transparent" "IgnoreProjector"="True" "RenderType"="Transparent" }
        LOD 100

        Pass
        {
            ZWrite Off
            Blend SrcAlpha OneMinusSrcAlpha

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            sampler2D _MainTex;
            float4 _MainTex_ST;
            sampler2D _PrevTex;
            float _FaceT;
            float _FaceMode;
            float _Overshoot;
            float _EyeY;
            float _EyeLX;
            float _EyeRX;
            float _BandMin;
            float _BandMax;

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float4 vertex : SV_POSITION;
                float2 uv : TEXCOORD0;
            };

            v2f vert(appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                float2 uv = i.uv;
                bool first = _FaceT < 0.5;
                float u = first ? 1.0 - _FaceT * 2.0 : (_FaceT - 0.5) * 2.0;
                bool pop = _FaceMode > 0.5;

                float s;
                if (pop)
                    s = max(u + (first ? 0.0 : _Overshoot * sin(u * UNITY_PI)), 0.001);
                else
                    s = max(u, 0.001);

                float2 suv;
                if (pop)
                {
                    float2 c = float2(uv.x < 0.5 ? _EyeLX : _EyeRX, _EyeY);
                    suv = c + (uv - c) / s;
                }
                else
                {
                    suv = float2(uv.x, _EyeY + (uv.y - _EyeY) / s);
                }

                fixed4 prevSample = tex2D(_PrevTex, suv);
                fixed4 mainSample = tex2D(_MainTex, suv);
                fixed4 bandCol = first ? prevSample : mainSample;
                bool inSuv = suv.y >= _BandMin && suv.y <= _BandMax && suv.x >= 0.0 && suv.x <= 1.0;
                bandCol.a = inSuv ? bandCol.a : 0.0;

                fixed4 outsideCol = lerp(tex2D(_PrevTex, uv), tex2D(_MainTex, uv), _FaceT);

                bool inBand = uv.y >= _BandMin && uv.y <= _BandMax;
                return inBand ? bandCol : outsideCol;
            }
            ENDCG
        }
    }
}
