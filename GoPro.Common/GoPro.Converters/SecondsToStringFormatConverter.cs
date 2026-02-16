using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class SecondsToStringFormatConverter : IValueConverter
	{
		public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
		{
			return TimeSpan.FromSeconds((double)(ulong)value * 1E-06).ToString("mm\\:ss");
		}

		public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
