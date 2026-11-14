import flet.testing as ftt


async def test_layout_sections(flet_app: ftt.FletTestApp):
    """Main layout shows input, result and history sections."""
    tester = flet_app.tester

    await tester.pump_and_settle()

    assert (await tester.find_by_text("Вход")).count == 1
    assert (await tester.find_by_text("Результат / превью")).count == 1
    assert (await tester.find_by_text("История")).count == 1
