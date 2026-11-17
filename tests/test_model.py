from multi_agent.model import Vortex


def test_vortex_model_steps():
    # Initialize the model
    model = Vortex(n_agents=2)

    # Run for a few steps
    for _ in range(10):
        model.step()

    # Check if the model is still running (or finished if small enough)
    # The important part is that it doesn't crash
    assert model.width > 0
    assert model.height > 0
    assert len(model.agents_by_type) > 0


if __name__ == "__main__":
    test_vortex_model_steps()
    print("Mesa model check passed!")
