using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class RatioToTimelineIconScaleConverter : IValueConverter
	{
		private double ICON_SCALE_MIN = 0.375;

		private double ICON_SCALE_MAX = 1.0;

		public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
		{
			double num = (double)value;
			return ICON_SCALE_MIN + num * (ICON_SCALE_MAX - ICON_SCALE_MIN);
		}

		public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
