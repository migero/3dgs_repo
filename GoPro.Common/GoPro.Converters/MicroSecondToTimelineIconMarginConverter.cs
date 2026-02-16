using System;
using System.Globalization;
using System.Windows;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class MicroSecondToTimelineIconMarginConverter : IMultiValueConverter
	{
		private double ICON_SCALE_MIN = 0.375;

		private double ICON_SCALE_MAX = 1.0;

		private double ICON_SIZE = 32.0;

		public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
		{
			//IL_0084: Unknown result type (might be due to invalid IL or missing references)
			ulong num = (ulong)values[0];
			ulong num2 = (ulong)values[1];
			double num3 = (double)values[2];
			double num4 = (double)values[3];
			double num5 = ICON_SCALE_MIN + (ICON_SCALE_MAX - ICON_SCALE_MIN) * num4;
			double num6 = (double)num / (double)num2;
			double num7 = num3 * num6 - ICON_SIZE * num5 * 0.5;
			double num8 = -6.0 + 10.0 * num4;
			return (object)new Thickness(num7, num8, 0.0, 0.0);
		}

		public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
