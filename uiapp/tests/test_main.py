import flet.testing as ftt


async def test_history_demo(flet_app: ftt.FletTestApp):
    """Compact history: tap demo button and assert an entry appears."""
    tester = flet_app.tester

    await tester.pump_and_settle()

    assert (await tester.find_by_text("История")).count == 1

    await tester.tap(await tester.find_by_text("Демо: событие"))
    await tester.pump_and_settle()

    assert (await tester.find_by_text("• Сгенерирован черновик плана")).count == 1
