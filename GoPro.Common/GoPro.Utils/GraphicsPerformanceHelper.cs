namespace GoPro.Utils
{
	public class GraphicsPerformanceHelper
	{
		public static void SetEnablePerformance(bool enabled)
		{
			int value = (enabled ? 1 : 0);
			ExportDll.SetVariableInt32("NvOptimusEnablement", value);
			ExportDll.SetVariableInt32("AmdPowerXpressRequestHighPerformance", value);
		}
	}
}
