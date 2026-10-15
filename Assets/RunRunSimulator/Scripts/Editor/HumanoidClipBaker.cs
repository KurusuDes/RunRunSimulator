using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

namespace MoriMonchiSimulator
{
public static class HumanoidClipBaker
{
    private const string Folder = "Assets/RunRunSimulator/Resources/Animations/Humans";
    private const int Samples = 24;
    private const float PlayerArmOpen = 0.38f;

    private delegate void PoseFn(float t, Pose p);

    private class Pose
    {
        public readonly Dictionary<string, float> Values = new();
        public float Bob;
        public void Set(string muscle, float v) => Values[muscle] = v;
        public void Add(string muscle, float v) => Values[muscle] = Get(muscle) + v;
        public float Get(string muscle) => Values.TryGetValue(muscle, out var v) ? v : 0f;
    }

    private static float Sin(float t, float cycles = 1f, float phase = 0f) => Mathf.Sin((t * cycles + phase) * Mathf.PI * 2f);
    private static float Cos(float t, float cycles = 1f, float phase = 0f) => Mathf.Cos((t * cycles + phase) * Mathf.PI * 2f);
    private static float Bump(float t, float center, float width) => Mathf.Clamp01(1f - Mathf.Abs(t - center) / width);
    private static float Smooth(float x) => x * x * (3f - 2f * x);

    [MenuItem("RunRunSimulator/Humans/Bake Clips")]
    public static void BakeAll()
    {
        EnsureFolder(Folder);

        var idle     = Bake("Human_Idle", 3f, true, IdlePose);
        var walk     = Bake("Human_Walk", 1.05f, true, WalkPose);
        var talk     = Bake("Human_Talk", 2.4f, true, TalkPose);
        var fpIdle   = Bake("FP_Idle", 3f, true, FpIdlePose);
        var fpWalk   = Bake("FP_Walk", 0.7f, true, FpWalkPose);
        var fpHold   = Bake("FP_Hold", 2.5f, true, FpHoldPose);
        var fpPet    = Bake("FP_Pet", 1.2f, true, FpPetPose);
        var fpThrow  = Bake("FP_Throw", 0.5f, false, FpThrowPose);
        var fpUse    = Bake("FP_Interact", 0.45f, false, FpInteractPose);
        var plIdle   = Bake("Player_Idle", 3f, true, PlayerIdlePose);
        var plWalk   = Bake("Player_Walk", 1.05f, true, PlayerWalkPose);

        BuildNpcController(idle, walk, talk);
        BuildFpController(fpIdle, fpWalk, fpHold, fpPet, fpThrow, fpUse);
        BuildPlayerBodyController(plIdle, plWalk);

        AssetDatabase.SaveAssets();
        Debug.Log("[HumanoidClipBaker] Baked 11 clips + HumanNpc/FPArms/PlayerBody controllers in " + Folder);
    }

    private static void Stand(Pose p)
    {
        foreach (var side in new[] { "Left", "Right" })
        {
            p.Set(side + " Upper Leg Front-Back", 0.6f);
            p.Set(side + " Upper Leg In-Out", 0.02f);
            p.Set(side + " Lower Leg Stretch", 0.96f);
            p.Set(side + " Foot Up-Down", 0.02f);
            p.Set(side + " Shoulder Down-Up", 0f);
            p.Set(side + " Arm Down-Up", -0.8f);
            p.Set(side + " Arm Front-Back", 0.05f);
            p.Set(side + " Arm Twist In-Out", 0.05f);
            p.Set(side + " Forearm Stretch", 0.85f);
            p.Set(side + " Forearm Twist In-Out", 0.1f);
            p.Set(side + " Hand Down-Up", 0f);
            Fingers(p, side, 0.35f, 0.2f);
        }
        p.Set("Jaw Close", 1f);
    }

    private static void Fingers(Pose p, string side, float curl, float spread)
    {
        foreach (var f in new[] { "Index", "Middle", "Ring", "Little" })
        {
            float extra = f == "Little" ? 0.1f : f == "Ring" ? 0.05f : 0f;
            p.Set(side + " " + f + " 1 Stretched", 1f - curl * 1.6f - extra);
            p.Set(side + " " + f + " 2 Stretched", 1f - curl * 1.9f - extra);
            p.Set(side + " " + f + " 3 Stretched", 1f - curl * 1.6f);
            p.Set(side + " " + f + " Spread", f == "Index" ? spread : f == "Middle" ? 0f : -spread);
        }
        p.Set(side + " Thumb 1 Stretched", -0.2f - curl * 0.4f);
        p.Set(side + " Thumb Spread", 0.3f);
        p.Set(side + " Thumb 2 Stretched", 0.6f - curl * 0.8f);
        p.Set(side + " Thumb 3 Stretched", 0.6f - curl * 0.8f);
    }

    private static void IdlePose(float t, Pose p)
    {
        Stand(p);
        float breath = Sin(t);
        p.Set("Chest Front-Back", -0.03f * breath);
        p.Set("UpperChest Front-Back", -0.02f * breath);
        p.Set("Spine Left-Right", 0.04f * Sin(t, 1f, 0.25f));
        p.Set("Head Nod Down-Up", 0.03f * breath);
        p.Add("Left Arm Down-Up", 0.015f * breath);
        p.Add("Right Arm Down-Up", 0.015f * breath);
        p.Bob = -0.004f * breath;
    }

    private static void WalkPose(float t, Pose p)
    {
        Stand(p);
        float s = Sin(t), c = Cos(t);
        p.Set("Left Upper Leg Front-Back", 0.6f + 0.38f * s);
        p.Set("Right Upper Leg Front-Back", 0.6f - 0.38f * s);
        p.Set("Left Lower Leg Stretch", 0.95f - 0.75f * Mathf.Pow(Mathf.Max(0f, -c), 1.5f));
        p.Set("Right Lower Leg Stretch", 0.95f - 0.75f * Mathf.Pow(Mathf.Max(0f, c), 1.5f));
        p.Set("Left Foot Up-Down", 0.05f + 0.2f * Mathf.Max(0f, -c) - 0.12f * Mathf.Max(0f, -s));
        p.Set("Right Foot Up-Down", 0.05f + 0.2f * Mathf.Max(0f, c) - 0.12f * Mathf.Max(0f, s));
        p.Set("Left Arm Front-Back", 0.05f - 0.3f * s);
        p.Set("Right Arm Front-Back", 0.05f + 0.3f * s);
        p.Set("Left Forearm Stretch", 0.8f - 0.25f * Mathf.Max(0f, s));
        p.Set("Right Forearm Stretch", 0.8f - 0.25f * Mathf.Max(0f, -s));
        p.Set("Spine Twist Left-Right", 0.07f * s);
        p.Set("Chest Twist Left-Right", -0.05f * s);
        p.Set("Spine Front-Back", 0.06f);
        p.Set("Head Nod Down-Up", -0.04f);
        p.Bob = -0.022f * Mathf.Abs(s);
    }

    private static void OpenArms(Pose p)
    {
        p.Add("Left Arm Down-Up", PlayerArmOpen);
        p.Add("Right Arm Down-Up", PlayerArmOpen);
    }

    private static void PlayerIdlePose(float t, Pose p)
    {
        IdlePose(t, p);
        OpenArms(p);
    }

    private static void PlayerWalkPose(float t, Pose p)
    {
        WalkPose(t, p);
        OpenArms(p);
    }

    private static void TalkPose(float t, Pose p)
    {
        IdlePose(t, p);
        float g = Smooth(Bump(t, 0.3f, 0.25f)) + Smooth(Bump(t, 0.72f, 0.2f)) * 0.7f;
        p.Set("Right Arm Front-Back", 0.05f - 0.5f * g);
        p.Set("Right Arm Down-Up", -0.8f + 0.35f * g);
        p.Set("Right Forearm Stretch", 0.85f - 0.8f * g);
        p.Set("Right Forearm Twist In-Out", 0.1f + 0.5f * g);
        Fingers(p, "Right", 0.35f - 0.3f * g, 0.2f + 0.3f * g);
        p.Set("Head Nod Down-Up", 0.06f * Sin(t, 3f));
        p.Set("Head Tilt Left-Right", 0.05f * Sin(t, 1f, 0.1f));
    }

    private static void Arm(Pose p, string side, float downUp, float frontBack, float forearm)
    {
        p.Set(side + " Arm Down-Up", downUp);
        p.Set(side + " Arm Front-Back", frontBack);
        p.Set(side + " Forearm Stretch", forearm);
    }

    private static void ArmLerp(Pose p, string side, Vector3 from, Vector3 to, float k) =>
        Arm(p, side, Mathf.Lerp(from.x, to.x, k), Mathf.Lerp(from.y, to.y, k), Mathf.Lerp(from.z, to.z, k));

    private static readonly Vector3 FpRest    = new(0f, -0.2f, 0.45f);
    private static readonly Vector3 FpCarry  = new(-0.1f, -0.6f, 0.9f);
    private static readonly Vector3 FpStroke  = new(-0.2f, -0.5f, 0.75f);
    private static readonly Vector3 FpReach   = new(-0.1f, -0.6f, 0.75f);
    private static readonly Vector3 FpWindUp  = new(0.4f, -0.2f, 0.45f);
    private static readonly Vector3 FpRelease = new(0f, -0.6f, 0.75f);

    private static void FpBase(Pose p)
    {
        Stand(p);
        foreach (var side in new[] { "Left", "Right" })
        {
            Arm(p, side, FpRest.x, FpRest.y, FpRest.z);
            p.Set(side + " Arm Twist In-Out", 0f);
            p.Set(side + " Forearm Twist In-Out", -0.5f);
            p.Set(side + " Hand Down-Up", -0.35f);
            Fingers(p, side, 0.45f, 0.1f);
        }
    }

    private static void FpLowered(Pose p)
    {
        Stand(p);
    }

    private static void FpIdlePose(float t, Pose p)
    {
        FpLowered(p);
        p.Add("Left Arm Down-Up", 0.025f * Sin(t));
        p.Add("Right Arm Down-Up", 0.025f * Sin(t, 1f, 0.12f));
        p.Add("Left Forearm Stretch", -0.03f * Sin(t, 1f, 0.05f));
        p.Add("Right Forearm Stretch", -0.03f * Sin(t, 1f, 0.17f));
    }

    private static void FpWalkPose(float t, Pose p)
    {
        FpLowered(p);
        float s = Sin(t);
        p.Add("Left Arm Front-Back", 0.15f * s);
        p.Add("Right Arm Front-Back", -0.15f * s);
        p.Bob = -0.01f * Mathf.Abs(s);
    }

    private static void FpHoldPose(float t, Pose p)
    {
        FpBase(p);
        float breath = Sin(t);
        foreach (var side in new[] { "Left", "Right" })
        {
            Arm(p, side, FpCarry.x + 0.015f * breath, FpCarry.y, FpCarry.z);
            p.Set(side + " Forearm Twist In-Out", 0.9f);
            p.Set(side + " Hand Down-Up", 0.3f);
            Fingers(p, side, 0.4f, 0.3f);
        }
    }

    private static void FpPetPose(float t, Pose p)
    {
        FpBase(p);
        float s = Sin(t);
        Arm(p, "Right", FpStroke.x + 0.05f * s, FpStroke.y - 0.08f * s, FpStroke.z);
        p.Set("Right Forearm Twist In-Out", -0.45f);
        p.Set("Right Hand Down-Up", -0.3f + 0.2f * Sin(t, 1f, 0.2f));
        Fingers(p, "Right", 0.06f + 0.06f * s, 0.25f);
        Arm(p, "Left", FpRest.x - 0.15f, FpRest.y + 0.15f, FpRest.z);
    }

    private static void FpThrowPose(float t, Pose p)
    {
        FpBase(p);
        float wind = Smooth(Mathf.Clamp01(t / 0.35f));
        float push = Smooth(Mathf.Clamp01((t - 0.35f) / 0.15f));
        float settle = Smooth(Mathf.Clamp01((t - 0.6f) / 0.4f));
        var pose = Vector3.Lerp(Vector3.Lerp(Vector3.Lerp(FpRest, FpWindUp, wind), FpRelease, push), FpRest, settle);
        Arm(p, "Right", pose.x, pose.y, pose.z);
        p.Set("Right Hand Down-Up", 0.1f + 0.3f * wind * (1f - push) - 0.4f * push * (1f - settle));
        Fingers(p, "Right", 0.3f - 0.25f * push * (1f - settle), 0.15f + 0.3f * push * (1f - settle));
        p.Add("Left Arm Front-Back", 0.15f * wind * (1f - settle));
    }

    private static void FpInteractPose(float t, Pose p)
    {
        FpBase(p);
        float reach = Smooth(Bump(t, 0.4f, 0.4f));
        ArmLerp(p, "Right", FpRest, FpReach, reach);
        p.Set("Right Hand Down-Up", 0.1f - 0.25f * reach);
        p.Set("Right Forearm Twist In-Out", -0.35f + 0.25f * reach);
        Fingers(p, "Right", 0.3f - 0.2f * reach, 0.15f + 0.15f * reach);
    }

    private static AnimationClip Bake(string name, float length, bool loop, PoseFn fn)
    {
        string path = $"{Folder}/{name}.anim";
        var clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(path);
        if (clip == null)
        {
            clip = new AnimationClip { name = name };
            AssetDatabase.CreateAsset(clip, path);
        }
        clip.ClearCurves();

        var curves = new Dictionary<string, AnimationCurve>();
        var rootY = new AnimationCurve();
        int keys = loop ? Samples : Samples + 1;
        for (int i = 0; i <= keys; i++)
        {
            float u = loop ? (float)(i % Samples) / Samples : (float)i / keys;
            float time = loop ? (float)i / Samples * length : u * length;
            var pose = new Pose();
            fn(u, pose);
            foreach (var kv in pose.Values)
            {
                if (!curves.TryGetValue(kv.Key, out var curve)) curves[kv.Key] = curve = new AnimationCurve();
                curve.AddKey(time, kv.Value);
            }
            rootY.AddKey(time, 1f + pose.Bob);
            if (!loop && i == keys) break;
        }

        foreach (var kv in curves)
        {
            Smoothen(kv.Value);
            AnimationUtility.SetEditorCurve(clip, EditorCurveBinding.FloatCurve("", typeof(Animator), AttributeName(kv.Key)), kv.Value);
        }
        Smoothen(rootY);
        AnimationUtility.SetEditorCurve(clip, EditorCurveBinding.FloatCurve("", typeof(Animator), "RootT.x"), AnimationCurve.Constant(0f, length, 0f));
        AnimationUtility.SetEditorCurve(clip, EditorCurveBinding.FloatCurve("", typeof(Animator), "RootT.y"), rootY);
        AnimationUtility.SetEditorCurve(clip, EditorCurveBinding.FloatCurve("", typeof(Animator), "RootT.z"), AnimationCurve.Constant(0f, length, 0f));
        AnimationUtility.SetEditorCurve(clip, EditorCurveBinding.FloatCurve("", typeof(Animator), "RootQ.x"), AnimationCurve.Constant(0f, length, 0f));
        AnimationUtility.SetEditorCurve(clip, EditorCurveBinding.FloatCurve("", typeof(Animator), "RootQ.y"), AnimationCurve.Constant(0f, length, 0f));
        AnimationUtility.SetEditorCurve(clip, EditorCurveBinding.FloatCurve("", typeof(Animator), "RootQ.z"), AnimationCurve.Constant(0f, length, 0f));
        AnimationUtility.SetEditorCurve(clip, EditorCurveBinding.FloatCurve("", typeof(Animator), "RootQ.w"), AnimationCurve.Constant(0f, length, 1f));

        var settings = AnimationUtility.GetAnimationClipSettings(clip);
        settings.loopTime = loop;
        settings.loopBlend = loop;
        settings.loopBlendOrientation = true;
        settings.loopBlendPositionY = true;
        settings.loopBlendPositionXZ = true;
        settings.keepOriginalOrientation = true;
        settings.keepOriginalPositionY = true;
        settings.keepOriginalPositionXZ = true;
        settings.heightFromFeet = false;
        AnimationUtility.SetAnimationClipSettings(clip, settings);
        EditorUtility.SetDirty(clip);
        return clip;
    }

    private static void Smoothen(AnimationCurve curve)
    {
        for (int i = 0; i < curve.length; i++) curve.SmoothTangents(i, 0f);
    }

    private static string AttributeName(string muscle)
    {
        foreach (var side in new[] { "Left", "Right" })
        foreach (var f in new[] { "Thumb", "Index", "Middle", "Ring", "Little" })
        {
            string prefix = side + " " + f + " ";
            if (muscle.StartsWith(prefix, StringComparison.Ordinal))
                return side + "Hand." + f + "." + muscle.Substring(prefix.Length);
        }
        return muscle;
    }

    private static void BuildNpcController(AnimationClip idle, AnimationClip walk, AnimationClip talk)
    {
        var ctrl = FreshController($"{Folder}/HumanNpc.controller");
        ctrl.AddParameter("Speed", AnimatorControllerParameterType.Float);
        ctrl.AddParameter("Talking", AnimatorControllerParameterType.Bool);
        var sm = ctrl.layers[0].stateMachine;

        var loco = BuildLocomotion(ctrl, idle, walk);

        var talkState = sm.AddState("Talk");
        talkState.motion = talk;
        var toTalk = loco.AddTransition(talkState);
        toTalk.hasExitTime = false; toTalk.duration = 0.25f;
        toTalk.AddCondition(AnimatorConditionMode.If, 0f, "Talking");
        var back = talkState.AddTransition(loco);
        back.hasExitTime = false; back.duration = 0.25f;
        back.AddCondition(AnimatorConditionMode.IfNot, 0f, "Talking");
        sm.defaultState = loco;
    }

    private static void BuildPlayerBodyController(AnimationClip idle, AnimationClip walk)
    {
        var ctrl = FreshController($"{Folder}/PlayerBody.controller");
        ctrl.AddParameter("Speed", AnimatorControllerParameterType.Float);
        ctrl.layers[0].stateMachine.defaultState = BuildLocomotion(ctrl, idle, walk);
    }

    private static AnimatorState BuildLocomotion(AnimatorController ctrl, AnimationClip idle, AnimationClip walk)
    {
        var loco = ctrl.CreateBlendTreeInController("Locomotion", out var tree, 0);
        tree.blendParameter = "Speed";
        tree.useAutomaticThresholds = false;
        tree.AddChild(idle, 0f);
        tree.AddChild(walk, 1.4f);
        tree.AddChild(walk, 3.6f);
        var children = tree.children;
        children[2].timeScale = 1.9f;
        tree.children = children;
        return loco;
    }

    private static void BuildFpController(AnimationClip idle, AnimationClip walk, AnimationClip hold, AnimationClip pet, AnimationClip thr, AnimationClip use)
    {
        var ctrl = FreshController($"{Folder}/FPArms.controller");
        ctrl.AddParameter("Speed", AnimatorControllerParameterType.Float);
        ctrl.AddParameter("Holding", AnimatorControllerParameterType.Bool);
        ctrl.AddParameter("Petting", AnimatorControllerParameterType.Bool);
        ctrl.AddParameter("Throw", AnimatorControllerParameterType.Trigger);
        ctrl.AddParameter("Interact", AnimatorControllerParameterType.Trigger);
        ctrl.AddParameter("Jump", AnimatorControllerParameterType.Trigger);

        var layers = ctrl.layers;
        layers[0].iKPass = true;
        ctrl.layers = layers;
        var sm = ctrl.layers[0].stateMachine;

        var loco = ctrl.CreateBlendTreeInController("Locomotion", out var tree, 0);
        tree.blendParameter = "Speed";
        tree.useAutomaticThresholds = false;
        tree.AddChild(idle, 0f);
        tree.AddChild(walk, 1f);

        var holdState = sm.AddState("Hold"); holdState.motion = hold;
        var petState = sm.AddState("Pet"); petState.motion = pet;
        var throwState = sm.AddState("Throw"); throwState.motion = thr;
        var useState = sm.AddState("Interact"); useState.motion = use;

        Link(loco, holdState, AnimatorConditionMode.If, "Holding", 0.25f);
        Link(holdState, loco, AnimatorConditionMode.IfNot, "Holding", 0.4f);
        Link(loco, petState, AnimatorConditionMode.If, "Petting", 0.25f);
        Link(petState, loco, AnimatorConditionMode.IfNot, "Petting", 0.4f);

        var anyThrow = sm.AddAnyStateTransition(throwState);
        anyThrow.hasExitTime = false; anyThrow.duration = 0.12f; anyThrow.canTransitionToSelf = false;
        anyThrow.AddCondition(AnimatorConditionMode.If, 0f, "Throw");
        var anyUse = sm.AddAnyStateTransition(useState);
        anyUse.hasExitTime = false; anyUse.duration = 0.15f; anyUse.canTransitionToSelf = false;
        anyUse.AddCondition(AnimatorConditionMode.If, 0f, "Interact");

        foreach (var oneShot in new[] { throwState, useState })
        {
            var back = oneShot.AddTransition(loco);
            back.hasExitTime = true; back.exitTime = 0.85f; back.duration = 0.35f;
        }
        sm.defaultState = loco;
    }

    private static AnimatorController FreshController(string path)
    {
        var ctrl = AssetDatabase.LoadAssetAtPath<AnimatorController>(path);
        if (ctrl == null) return AnimatorController.CreateAnimatorControllerAtPath(path);

        ctrl.parameters = new AnimatorControllerParameter[0];
        var sm = ctrl.layers[0].stateMachine;
        foreach (var t in sm.anyStateTransitions) sm.RemoveAnyStateTransition(t);
        foreach (var child in sm.states) sm.RemoveState(child.state);
        foreach (var sub in AssetDatabase.LoadAllAssetsAtPath(path))
            if (sub is BlendTree) UnityEngine.Object.DestroyImmediate(sub, true);
        return ctrl;
    }

    private static void Link(AnimatorState from, AnimatorState to, AnimatorConditionMode mode, string param, float duration)
    {
        var tr = from.AddTransition(to);
        tr.hasExitTime = false;
        tr.duration = duration;
        tr.AddCondition(mode, 0f, param);
    }

    private static void EnsureFolder(string folder)
    {
        if (AssetDatabase.IsValidFolder(folder)) return;
        int slash = folder.LastIndexOf('/');
        EnsureFolder(folder.Substring(0, slash));
        AssetDatabase.CreateFolder(folder.Substring(0, slash), folder.Substring(slash + 1));
    }
}
}
