using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class MicroSecondToTime : IValueConverter
	{
		public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
		{
			if (value != null)
			{
				TimeSpan timeSpan = TimeSpan.FromMilliseconds((double)(ulong)value * 0.001);
				return string.Format("{0,2:D2}", (int)timeSpan.TotalHours) + timeSpan.ToString("\\:mm\\:ss\\.ffff");
			}
			return null;
		}

		public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
