using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class NumericToStringConverter : IValueConverter
	{
		public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
		{
			return value?.ToString();
		}

		public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
		{
			if (value == null)
			{
				return null;
			}
			double result2;
			if (targetType == typeof(ulong?) || targetType == typeof(ulong))
			{
				ulong result = 0uL;
				if (ulong.TryParse((string)value, out result))
				{
					return result;
				}
			}
			else if ((targetType == typeof(double?) || targetType == typeof(double)) && double.TryParse((string)value, out result2))
			{
				return result2;
			}
			return null;
		}
	}
}
