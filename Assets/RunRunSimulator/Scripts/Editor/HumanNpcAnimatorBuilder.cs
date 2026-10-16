using System.Collections.Generic;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

namespace MoriMonchiSimulator
{
    public static class HumanNpcAnimatorBuilder
    {
        private const string Folder = "Assets/RunRunSimulator/Resources/Animations/Humans";
        private const string ControllerPath = Folder + "/HumanNpcSK.controller";
        private const string OverridePath = Folder + "/HumanNpcSK_Femn.overrideController";

        private static readonly string[] SearchFolders =
        {
            "Assets/Synty/AnimationBaseLocomotion",
            "Assets/Synty/AnimationIdles",
            "Assets/Synty/AnimationEmotesAndTaunts",
            Folder + "/Sidekick"
        };

        private static readonly string[] MascNames =
        {
            "A_MOD_IDL_Idle_Base_Masc",
            "A_MOD_BL_Walk_F_Masc",
            "A_MOD_BL_Run_F_Masc",
            "A_MOD_IDL_Thoughtful_L_Loop_Masc",
            "A_MOD_IDL_ArmsFolded_Casual_Loop_Masc",
            "A_MOD_IDL_HandsOnHips_Base_Loop_Masc",
            "A_MM_Pay_Masc",
            "A_MOD_EMOT_Happy_ThumbsUp_Masc",
            "A_MOD_EMOT_Reproach_WaveAway_Masc"
        };

        private const int LoopCount = 6;

        [MenuItem("RunRunSimulator/Humans/Build NPC Animator")]
        public static void Build()
        {
            var index = IndexClips();
            var masc = new AnimationClip[MascNames.Length];
            var missing = new List<string>();
            for (int i = 0; i < MascNames.Length; i++)
            {
                masc[i] = Resolve(index, MascNames[i], i < LoopCount);
                if (masc[i] == null) missing.Add(MascNames[i]);
            }

            if (missing.Count > 0)
            {
                Debug.LogError($"[HumanNpcAnimatorBuilder] Faltan clips masculinos, abortado: {string.Join(", ", missing)}");
                return;
            }

            var femn = new AnimationClip[MascNames.Length];
            int femnFound = 0;
            var femnMissing = new List<string>();
            for (int i = 0; i < MascNames.Length; i++)
            {
                string femnName = MascNames[i].Substring(0, MascNames[i].Length - "_Masc".Length) + "_Femn";
                femn[i] = Resolve(index, femnName, i < LoopCount);
                if (femn[i] != null) femnFound++;
                else femnMissing.Add(femnName);
            }

            EnsureFolder(Folder);
            var ctrl = BuildController(masc);
            BuildOverride(ctrl, masc, femn, femnMissing);
            AssetDatabase.SaveAssets();
            Debug.Log($"[HumanNpcAnimatorBuilder] Masc {masc.Length}/{MascNames.Length}, Femn {femnFound}/{MascNames.Length}, faltan Femn: {femnMissing.Count}");
        }

        private static Dictionary<string, AnimationClip> IndexClips()
        {
            var index = new Dictionary<string, AnimationClip>();
            var existing = new List<string>();
            foreach (var f in SearchFolders)
                if (AssetDatabase.IsValidFolder(f)) existing.Add(f);
            if (existing.Count == 0) return index;

            var seen = new HashSet<string>();
            foreach (var guid in AssetDatabase.FindAssets("t:Model", existing.ToArray()))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (!seen.Add(path)) continue;
                foreach (var obj in AssetDatabase.LoadAllAssetsAtPath(path))
                {
                    if (obj is AnimationClip clip && !clip.name.StartsWith("__preview__") && !index.ContainsKey(clip.name))
                        index[clip.name] = clip;
                }
            }
            return index;
        }

        private static AnimationClip Resolve(Dictionary<string, AnimationClip> index, string name, bool mustLoop)
        {
            if (!index.TryGetValue(name, out var clip) || clip == null) return null;
            if (!mustLoop || clip.isLooping) return clip;

            string path = AssetDatabase.GetAssetPath(clip);
            if (AssetImporter.GetAtPath(path) is ModelImporter importer)
            {
                var anims = importer.clipAnimations;
                if (anims == null || anims.Length == 0) anims = importer.defaultClipAnimations;
                for (int i = 0; i < anims.Length; i++)
                    if (anims[i].name == name) anims[i].loopTime = true;
                importer.clipAnimations = anims;
                importer.SaveAndReimport();
                foreach (var obj in AssetDatabase.LoadAllAssetsAtPath(path))
                {
                    if (obj is AnimationClip reloaded && reloaded.name == name)
                    {
                        index[name] = reloaded;
                        return reloaded;
                    }
                }
            }
            return clip;
        }

        private static AnimatorController BuildController(AnimationClip[] c)
        {
            var ctrl = FreshController(ControllerPath);
            ctrl.AddParameter("Speed", AnimatorControllerParameterType.Float);
            ctrl.AddParameter("State", AnimatorControllerParameterType.Int);
            ctrl.AddParameter("Pay", AnimatorControllerParameterType.Trigger);
            ctrl.AddParameter("Upset", AnimatorControllerParameterType.Trigger);
            var sm = ctrl.layers[0].stateMachine;

            var loco = ctrl.CreateBlendTreeInController("Locomotion", out var tree, 0);
            tree.blendParameter = "Speed";
            tree.useAutomaticThresholds = false;
            tree.AddChild(c[0], 0f);
            tree.AddChild(c[1], 1.4f);
            tree.AddChild(c[2], 3.6f);
            sm.defaultState = loco;

            AddLoopState(sm, loco, "Browse", c[3], 1);
            AddLoopState(sm, loco, "Queue", c[4], 2);
            AddLoopState(sm, loco, "Talk", c[5], 3);

            var pay = sm.AddState("Pay"); pay.motion = c[6];
            var happy = sm.AddState("Happy"); happy.motion = c[7];
            var upset = sm.AddState("Upset"); upset.motion = c[8];

            AnyTrigger(sm, pay, "Pay");
            AnyTrigger(sm, upset, "Upset");

            var payToHappy = pay.AddTransition(happy);
            payToHappy.hasExitTime = true; payToHappy.exitTime = 0.9f; payToHappy.duration = 0.15f;

            var happyBack = happy.AddTransition(loco);
            happyBack.hasExitTime = true; happyBack.exitTime = 0.92f; happyBack.duration = 0.25f;

            var upsetBack = upset.AddTransition(loco);
            upsetBack.hasExitTime = true; upsetBack.exitTime = 0.92f; upsetBack.duration = 0.25f;

            EditorUtility.SetDirty(ctrl);
            return ctrl;
        }

        private static void AddLoopState(AnimatorStateMachine sm, AnimatorState loco, string name, AnimationClip clip, int value)
        {
            var state = sm.AddState(name);
            state.motion = clip;
            var to = loco.AddTransition(state);
            to.hasExitTime = false; to.duration = 0.25f;
            to.AddCondition(AnimatorConditionMode.Equals, value, "State");
            var back = state.AddTransition(loco);
            back.hasExitTime = false; back.duration = 0.25f;
            back.AddCondition(AnimatorConditionMode.NotEqual, value, "State");
        }

        private static void AnyTrigger(AnimatorStateMachine sm, AnimatorState target, string trigger)
        {
            var t = sm.AddAnyStateTransition(target);
            t.hasExitTime = false; t.duration = 0.15f;
            t.canTransitionToSelf = false;
            t.AddCondition(AnimatorConditionMode.If, 0f, trigger);
        }

        private static void BuildOverride(AnimatorController ctrl, AnimationClip[] masc, AnimationClip[] femn, List<string> femnMissing)
        {
            var ov = AssetDatabase.LoadAssetAtPath<AnimatorOverrideController>(OverridePath);
            if (ov == null)
            {
                ov = new AnimatorOverrideController(ctrl);
                AssetDatabase.CreateAsset(ov, OverridePath);
            }
            ov.runtimeAnimatorController = ctrl;

            var map = new Dictionary<AnimationClip, AnimationClip>();
            for (int i = 0; i < masc.Length; i++)
            {
                if (femn[i] == null)
                {
                    Debug.LogWarning($"[HumanNpcAnimatorBuilder] Falta par femenino {femnMissing.Find(n => n.StartsWith(MascNames[i].Substring(0, MascNames[i].Length - 5)))}, se deja el masculino");
                    continue;
                }
                map[masc[i]] = femn[i];
            }

            var pairs = new List<KeyValuePair<AnimationClip, AnimationClip>>();
            ov.GetOverrides(pairs);
            for (int i = 0; i < pairs.Count; i++)
            {
                var original = pairs[i].Key;
                pairs[i] = new KeyValuePair<AnimationClip, AnimationClip>(original, map.TryGetValue(original, out var replacement) ? replacement : null);
            }
            ov.ApplyOverrides(pairs);
            EditorUtility.SetDirty(ov);
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
                if (sub is BlendTree) Object.DestroyImmediate(sub, true);
            return ctrl;
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
