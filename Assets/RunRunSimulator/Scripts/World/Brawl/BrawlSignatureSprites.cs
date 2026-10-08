using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlSignatureSprites
{
    private readonly Transform root;
    private readonly Stack<SpriteRenderer> freeSprites = new();
    private readonly Stack<Light> freeLights = new();

    public BrawlSignatureSprites(Transform root)
    {
        this.root = root;
    }

    public SpriteRenderer AcquireSprite(Sprite sprite, Material material, int order)
    {
        SpriteRenderer sr;
        if (freeSprites.Count > 0)
        {
            sr = freeSprites.Pop();
        }
        else
        {
            var go = new GameObject("SignatureSprite");
            go.transform.SetParent(root, false);
            sr = go.AddComponent<SpriteRenderer>();
            sr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            sr.receiveShadows = false;
        }

        sr.sprite = sprite;
        sr.sharedMaterial = material;
        sr.sortingOrder = order;
        sr.color = Color.white;
        sr.transform.localScale = Vector3.zero;
        sr.gameObject.SetActive(true);
        return sr;
    }

    public void ReleaseSprite(SpriteRenderer sr)
    {
        if (sr == null) return;
        sr.gameObject.SetActive(false);
        freeSprites.Push(sr);
    }

    public Light AcquireLight(float range)
    {
        Light light;
        if (freeLights.Count > 0)
        {
            light = freeLights.Pop();
        }
        else
        {
            var go = new GameObject("SignatureLight");
            go.transform.SetParent(root, false);
            light = go.AddComponent<Light>();
            light.type = LightType.Point;
            light.shadows = LightShadows.None;
        }

        light.range = range;
        light.intensity = 0f;
        light.gameObject.SetActive(true);
        return light;
    }

    public void ReleaseLight(Light light)
    {
        if (light == null) return;
        light.gameObject.SetActive(false);
        freeLights.Push(light);
    }
}
}
