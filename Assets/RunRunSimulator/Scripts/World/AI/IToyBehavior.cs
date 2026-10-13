namespace MoriMonchiSimulator
{

internal interface IToyBehavior
{
    bool IsActive { get; }
    CreatureIntent Intent { get; }
    bool TryEngage(ToyTuningSO t);
    void Tick(ToyTuningSO t, float dt);
    bool ReactToHit(Toy hitToy, MoriMochiAgent kicker);
    void Clear();
}
}
