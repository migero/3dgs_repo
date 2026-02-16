using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class NormalizedDoubleToPercentage : IValueConverter
	{
		public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
		{
			return (int)((double)value * 100.0);
		}

		public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
