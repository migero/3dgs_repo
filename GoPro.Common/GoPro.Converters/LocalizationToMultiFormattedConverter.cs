using System;
using System.Globalization;
using System.Windows.Data;
using GoPro.Instance;

namespace GoPro.Converters
{
	public class LocalizationToMultiFormattedConverter : IMultiValueConverter
	{
		public object Convert(object[] value, Type targetType, object parameter, CultureInfo culture)
		{
			return string.Format(LocalizationService.Instance[(string)parameter], value);
		}

		public object[] ConvertBack(object value, Type[] targetType, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
