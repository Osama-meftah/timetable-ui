class ApiEndpoints {
  static BASE_API_URL = "http://127.0.0.1:8001/api/";

  static login = "login/";
  static logout = "logout/";
  static user = "user/";
  static sendResetEmail = "send_reseat_email/";
  static sendForgetPasswordEmail = "send_forget_password_email/";
  static resetTeacherPassword = "reset-password/";
  static departments = "departments/";
  static departmentsUpload = "uploadDepartments/";
  static programsUpload = "uploadPrograms/";
  static levelsUpload = "uploadLevels/";
  static todays = "todays/";
  static periods = "periods/";
  static halls = "halls/";
  static uploadHalls = "uploadHalls/";
  static tables = "tables/";
  static programs = "programs/";
  static levels = "levels/";
  static groups = "groups/";
  static teachers = "teachers/";
  static teachersUpload = "teachersUpload/";
  static teacherTimes = "teacherTimes/";
  static searchTeachersTimes = "searchteacherstimes/";
  static subjects = "subjects/";
  static uploadSubjects = "uploadSubjects/";
  static distributions = "distributions/";
  static lectures = "lectures/";
  static searchTeachers = "searchteachers/";

  static getUrl(endpoint) {
    return this.BASE_API_URL + endpoint;
  }
}

class AxiosCrudService {
  constructor(baseURL = ApiEndpoints.BASE_API_URL) {
    this.axiosInstance = axios.create({
      baseURL,
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
    });
  }

  // هذه الدالة مسؤولة عن عرض الرسائل
  showToast(message, type = "info") {
    if (typeof showMessageModal === "function") {
      showMessageModal(message, type);
    } else {
      // Fallback in case the function is not available
      alert(`${type.toUpperCase()}: ${message}`);
    }
  }

  extractMessage(responseOrError, defaultMsg) {
    try {
      if (responseOrError?.data?.message) {
        return responseOrError.data.message;
      } else if (responseOrError?.response?.data?.message) {
        return responseOrError.response.data.message;
      } else if (typeof responseOrError === "string") {
        return responseOrError;
      } else if (responseOrError?.response?.data) {
        return Object.values(responseOrError.response.data)[0];
      }
    } catch (_) {}
    return defaultMsg;
  }

  create(endpoint, data, renderRowCallback, tableBodyElement) {
    return this.axiosInstance
      .post(endpoint, data)
      .then((response) => {
        if (renderRowCallback && tableBodyElement) {
          const row = renderRowCallback(response.data);
          tableBodyElement.appendChild(row);
        }
        const msg = this.extractMessage(response, "تمت الإضافة بنجاح");
        this.showToast(msg, "success"); // <-- عرض رسالة النجاح
        return response;
      })
      .catch((error) => {
        const msg = this.extractMessage(error, "فشل في الإضافة");
        this.showToast(msg, "error"); // <-- عرض رسالة الخطأ
        throw error;
      });
  }

  update(endpoint, data, renderRowCallback, rowId) {
    return this.axiosInstance
      .put(endpoint, data)
      .then((response) => {
        if (renderRowCallback && rowId) {
          const oldRow = document.getElementById(rowId);
          if (oldRow) {
            const newRow = renderRowCallback(response.data);
            oldRow.replaceWith(newRow);
          }
        }
        const msg = this.extractMessage(response, "تم التعديل بنجاح");
        this.showToast(msg, "success"); // <-- عرض رسالة النجاح
        return response;
      })
      .catch((error) => {
        const msg = this.extractMessage(error, "فشل في التعديل");
        this.showToast(msg, "error"); // <-- عرض رسالة الخطأ
        throw error;
      });
  }

  delete(endpoint, rowId) {
    return this.axiosInstance
      .delete(endpoint)
      .then((response) => {
        if (rowId) {
          const row = document.getElementById(rowId);
          if (row) row.remove();
        }
        const msg = this.extractMessage(response, "تم الحذف بنجاح");
        this.showToast(msg, "success"); // <-- عرض رسالة النجاح
        return response;
      })
      .catch((error) => {
        const msg = this.extractMessage(error, "فشل في الحذف");
        this.showToast(msg, "error"); // <-- عرض رسالة الخطأ
        throw error;
      });
  }
}
