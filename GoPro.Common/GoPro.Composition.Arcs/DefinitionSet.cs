namespace GoPro.Composition.Arcs
{
	internal static class DefinitionSet
	{
		internal const double MaxAngle = 360.0;

		internal static double NormalizeAngle(double value)
		{
			if (value < 0.0)
			{
				return 0.0;
			}
			if (value > 360.0)
			{
				return 360.0;
			}
			return value;
		}
	}
}
