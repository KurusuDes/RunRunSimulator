using UnityEditor;
using UnityEngine;

namespace MoriMonchiSimulator
{
    [CustomEditor(typeof(ModularBuilding))]
    public class ModularBuildingEditor : Sirenix.OdinInspector.Editor.OdinEditor
    {
        public override void OnInspectorGUI()
        {
            base.OnInspectorGUI();

            EditorGUILayout.Space();
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Armar"))
            {
                Undo.SetCurrentGroupName("Armar edificio modular");
                int group = Undo.GetCurrentGroup();
                foreach (var t in targets) ModularBuildingBuilder.Build((ModularBuilding)t);
                Undo.CollapseUndoOperations(group);
            }
            if (GUILayout.Button("Limpiar"))
            {
                Undo.SetCurrentGroupName("Limpiar edificio modular");
                int group = Undo.GetCurrentGroup();
                foreach (var t in targets) ModularBuildingBuilder.Clear((ModularBuilding)t);
                Undo.CollapseUndoOperations(group);
            }
            EditorGUILayout.EndHorizontal();
        }
    }
}
