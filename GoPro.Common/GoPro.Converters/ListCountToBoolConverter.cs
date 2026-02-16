using System;
using System.Collections;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class ListCountToBoolConverter : IValueConverter
	{
		public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
		{
			if (value == null)
			{
				return false;
			}
			IList obj = (IList)value;
			int num = int.Parse((string)parameter);
			return obj.Count != num;
		}

		public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
