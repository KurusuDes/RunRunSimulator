using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.UIElements;

namespace MoriMonchiSimulator
{
    [RequireComponent(typeof(UIDocument))]
    public class EggLabPanel : MonoBehaviour
    {
        [Required, SerializeField] private EggLabBuilder builder;
        [Required, SerializeField] private EggLabPortrait portrait;
        [Required, SerializeField] private Camera worldCamera;

        private static readonly Color TealFill = new Color(51f / 255f, 191f / 255f, 166f / 255f);

        private VisualElement root;
        private VisualElement labelsContainer;
        private Button rearmButton;

        private VisualElement card;
        private Button cardCloseButton;
        private Label cardTitle;
        private VisualElement portraitElement;
        private VisualElement motherSwatch;
        private Label motherName;
        private VisualElement fatherSwatch;
        private Label fatherName;
        private VisualElement radialContainer;
        private RadialSlot radial;
        private Label radialPercent;
        private Label costLabel;

        private readonly List<(Button button, EggLabEntry entry)> numberButtons = new();

        private void OnEnable()
        {
            root = GetComponent<UIDocument>().rootVisualElement;
            labelsContainer = root.Q("egg-lab__labels");
            rearmButton = root.Q<Button>("egg-lab__rearm");

            card = root.Q("egg-lab__card");
            cardCloseButton = root.Q<Button>("egg-lab__card-close");
            cardTitle = root.Q<Label>("egg-lab__card-title");
            portraitElement = root.Q("egg-lab__portrait");
            motherSwatch = root.Q("egg-lab__mother-swatch");
            motherName = root.Q<Label>("egg-lab__mother-name");
            fatherSwatch = root.Q("egg-lab__father-swatch");
            fatherName = root.Q<Label>("egg-lab__father-name");
            radialContainer = root.Q("egg-lab__radial");
            costLabel = root.Q<Label>("egg-lab__cost");

            if (radialContainer != null)
            {
                radialContainer.Clear();
                radial = new RadialSlot();
                radial.AddToClassList("egg-lab__radial-fill");
                radial.FillColor = TealFill;
                radialContainer.Add(radial);

                radialPercent = new Label();
                radialPercent.pickingMode = PickingMode.Ignore;
                radialPercent.AddToClassList("egg-lab__radial-percent");
                radialContainer.Add(radialPercent);
            }

            if (builder != null)
            {
                builder.Rebuilt += OnRebuilt;
                builder.Selected += OnSelected;
            }

            if (rearmButton != null) rearmButton.clicked += OnRearmClicked;
            if (cardCloseButton != null) cardCloseButton.clicked += CloseCard;

            RebuildLabels();
            CloseCard();
        }

        private void OnDisable()
        {
            if (builder != null)
            {
                builder.Rebuilt -= OnRebuilt;
                builder.Selected -= OnSelected;
            }

            if (rearmButton != null) rearmButton.clicked -= OnRearmClicked;
            if (cardCloseButton != null) cardCloseButton.clicked -= CloseCard;

            ClearNumberButtons();
        }

        private void OnRebuilt()
        {
            CloseCard();
            RebuildLabels();
        }

        private void RebuildLabels()
        {
            ClearNumberButtons();
            if (builder == null || labelsContainer == null) return;

            foreach (var entry in builder.Entries)
            {
                var capturedEntry = entry;
                var button = new Button(() => builder.Select(capturedEntry)) { text = capturedEntry.Number.ToString() };
                button.AddToClassList("egg-lab__num");
                labelsContainer.Add(button);
                numberButtons.Add((button, capturedEntry));
            }
        }

        private void ClearNumberButtons()
        {
            labelsContainer?.Clear();
            numberButtons.Clear();
        }

        private void OnRearmClicked()
        {
            builder.Rebuild();
        }

        private void OnSelected(EggLabEntry entry)
        {
            if (card == null || entry == null) return;

            card.style.display = DisplayStyle.Flex;

            if (cardTitle != null) cardTitle.text = $"Huevo #{entry.Number}";

            if (portraitElement != null && portrait != null && entry.Root != null)
            {
                var rt = portrait.Show(entry.Root);
                portraitElement.style.backgroundImage = new StyleBackground(Background.FromRenderTexture(rt));
                portraitElement.style.backgroundColor = Color.clear;
                portraitElement.style.backgroundSize = new BackgroundSize(BackgroundSizeType.Contain);
            }

            SetParent(motherSwatch, motherName, entry.Mother, "♀");
            SetParent(fatherSwatch, fatherName, entry.Father, "♂");

            if (radial != null) radial.Charge01 = entry.Progress01;
            if (radialPercent != null)
                radialPercent.text = entry.Progress01 >= 1f ? "¡Listo!" : Mathf.RoundToInt(entry.Progress01 * 100f) + "%";

            if (costLabel != null) costLabel.text = $"Minerita {entry.HatchCost}";
        }

        private static void SetParent(VisualElement swatch, Label label, CreatureDNA dna, string glyph)
        {
            if (swatch != null) swatch.style.backgroundColor = dna != null ? dna.BaseColor : Color.clear;
            if (label != null) label.text = glyph + " " + (dna != null && !string.IsNullOrEmpty(dna.CustomName) ? dna.CustomName : "?");
        }

        private void CloseCard()
        {
            portrait?.Hide();
            if (card != null) card.style.display = DisplayStyle.None;
        }

        private void LateUpdate()
        {
            if (root == null || worldCamera == null) return;

            var panel = root.panel;
            if (panel == null) return;

            for (int i = 0; i < numberButtons.Count; i++)
            {
                var (button, entry) = numberButtons[i];
                if (button == null || entry.Root == null) continue;

                Vector3 worldPos = entry.Root.position + Vector3.up * 0.42f;
                Vector3 toPoint = worldPos - worldCamera.transform.position;
                bool behind = Vector3.Dot(worldCamera.transform.forward, toPoint) <= 0f;
                if (behind)
                {
                    button.style.display = DisplayStyle.None;
                    continue;
                }

                button.style.display = DisplayStyle.Flex;
                Vector2 panelPos = RuntimePanelUtils.CameraTransformWorldToPanel(panel, worldPos, worldCamera);
                button.style.left = panelPos.x;
                button.style.top = panelPos.y;
            }
        }
    }
}
